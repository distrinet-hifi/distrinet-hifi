#!/usr/bin/env python
# coding: utf-8

# In[10]:


from asynciojobs import Scheduler
from apssh import SshNode, SshJob, Run, RunString, Push, Pull


# In[11]:


HOSTNAME = 'faraday.inria.fr'
SLICE = 'inria_distrinet'
NODES = ['fit01', 'fit03', 'fit06', 'fit07']
LEADER = NODES[0]
WORKERS = NODES[1:]
PATH = 'data/'


# In[12]:


faraday = SshNode(hostname=HOSTNAME, username=SLICE, verbose=False)
nodes = {node_name: SshNode(gateway=faraday, hostname=node_name, username='root', verbose=False) for node_name in NODES}
scheduler = Scheduler()


# In[ ]:


check_lease = SshJob (
    node = faraday,
    critical = True,
    command = Run('rleases --check'),
    scheduler = scheduler
)

load_images = SshJob (
    node = faraday,
    commands = [
        Run("rload -i u18.04-distrinet_hifi_leader %s" % LEADER),
        Run("rload -i u18.04-distrinet_hifi_worker %s" % ' '.join(WORKERS)),
        Run("rwait %s" % ' '.join(NODES)),
        Run("sleep 60")
    ],
    required = check_lease,
    scheduler = scheduler
)


# In[ ]:


net_intfs = {}
for node_name in NODES:
    node = nodes[node_name]
    ip_address = '10.10.20.%s/24' % node_name[-1:]
    net_intf = SshJob (
        node = node,
        command = Run('ifconfig', 'data', ip_address, 'up'),
        required = load_images,
        scheduler = scheduler
    )
    net_intfs[node_name] = net_intf


# In[ ]:


monitoring_agents = {}
for node_name in NODES:
    node = nodes[node_name]
    ip_address = '10.10.20.%s/24' % node_name[-1:]
    monitoring_agent = SshJob (
        node = node,
        command = Run('cd /root/experiment/ ;',
                      'nohup python3 /root/experiment/agent.py',
                      '--ip=10.10.20.%s' % node_name[-1:],
                      '--bastion=10.10.20.%s' % LEADER[-1:],
                      '> agent.out 2>&1 < /dev/null &'
                     ),
        required = net_intfs[node_name],
        scheduler = scheduler
    )
    monitoring_agents[node_name] = monitoring_agent


# In[ ]:


of_controller = SshJob (
        node = nodes[LEADER],
        command = Run('nohup ryu-manager', 
                      '/usr/lib/python3/dist-packages/ryu/app/simple_switch_stp_13.py',
                      '> ryu.out 2>&1 < /dev/null &'),
        required = net_intfs[LEADER],
        scheduler = scheduler
    )


# In[9]:


experiment = SshJob (
        node = nodes[LEADER],
        commands = [
            Run('cd ~/Distrinet/mininet/ ;', 
                'export PYTHONPATH=$PYTHONPATH:mininet: ;',
                'python3 bin/dmn',
                '--bastion=10.10.20.%s' % LEADER[-1:],
                '--workers="%s"' % ','.join(['10.10.20.%s' % node_name[-1:] for node_name in NODES]),
                '--custom=custom/experiment.py',
                '--controller=lxcremote,ip=192.168.0.1',
                '--mapper=expmapper',
                '--topo=exptopo,5,10,4',
                '--test=experiment,100M,200'
            ),
            Run('pkill -SIGKILL ryu')
        ],
        required = [of_controller]+list(monitoring_agents.values()),
        scheduler = scheduler
    )


# In[ ]:


download = SshJob (
        node = nodes[LEADER],
        command = Pull(remotepaths=['/root/results'], localpath=PATH, recurse=True),
        required = experiment,
        scheduler = scheduler
    )

ok = scheduler.orchestrate()

