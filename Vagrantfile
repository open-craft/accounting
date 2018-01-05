Vagrant.configure("2") do |config|
    config.vm.box = "ubuntu/trusty64"

  config.vm.synced_folder '.', '/vagrant', disabled: true
  config.vm.synced_folder '.', '/home/vagrant/opencraft'

  config.vm.network :forwarded_port, guest: 1786, host: 1786 
  
  config.ssh.forward_x11 = true
  config.vm.provision 'shell',
                      path: 'bin/setup',
                      privileged: false,
                      keep_color: true
end

