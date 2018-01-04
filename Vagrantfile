Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/trusty64"

  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.vm.synced_folder '.', '/home/vagrant/opencraft'

  # The url from where the 'config.vm.box' box will be fetched if it
  # doesn't already exist on the user's system.
  #config.vm.box_url = "http://files.vagrantup.com/precise32.box"

  #config.vm.network 'forwarded_port', guest: 2001, host: 2001
  #config.vm.network 'forwarded_port', guest: 5000, host: 5000
  #config.vm.network 'forwarded_port', guest: 8888, host: 8888

  
  config.ssh.forward_x11 = true
  config.vm.provision 'shell',
                      path: 'bin/setup',
                      privileged: false,
                      keep_color: true
end

