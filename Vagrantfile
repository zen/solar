# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"
SLAVES_COUNT = 2
ANSIBLE_CONFIG_PATH = "/etc/ansible"
ANSIBLE_CONFIG_FILE = "ansible.cfg"
ANSIBLE_LOG = "/var/log/ansible.log"

config = "#{ANSIBLE_CONFIG_PATH}/#{ANSIBLE_CONFIG_FILE}"

init_script = <<SCRIPT
apt-get -y install python-pip python-dev
pip install ansible
mkdir -p "#{ANSIBLE_CONFIG_PATH}"
echo "[defaults]" > "#{config}"
echo "log_path = #{ANSIBLE_LOG}" >> "#{config}"
ansible-playbook -v -i "localhost," -c local /vagrant/main.yml /vagrant/docker.yml
SCRIPT

slave_script = <<SCRIPT
apt-get -y install python-pip python-dev
pip install ansible
mkdir -p "#{ANSIBLE_CONFIG_PATH}"
echo "[defaults]" > "#{config}"
echo "log_path = #{ANSIBLE_LOG}" >> "#{config}"
ansible-playbook -v -i "localhost," -c local /vagrant/main.yml /vagrant/docker.yml /vagrant/slave.yml /vagrant/slave_cinder.yml
apt-get update
apt-get -y upgrade
add-apt-repository -y cloud-archive:juno
apt-get update || apt-get update --fix-missing
SCRIPT

master_celery = <<SCRIPT
ansible-playbook -i "localhost," -c local /vagrant/celery.yml --skip-tags slave
SCRIPT

slave_celery = <<SCRIPT
ansible-playbook -i "localhost," -c local /vagrant/celery.yml --skip-tags master
SCRIPT

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  #config.vm.box = "deb/jessie-amd64"
  #config.vm.box = "rustyrobot/deb-jessie-amd64"
  config.vm.box = "ubuntu/trusty64"

  config.vm.define "solar-dev", primary: true do |config|
    config.vm.provision "shell", inline: init_script, privileged: true
    config.vm.provision "shell", inline: master_celery, privileged: true
    config.vm.provision "file", source: "~/.vagrant.d/insecure_private_key", destination: "/vagrant/tmp/keys/ssh_private"
    config.vm.provision "file", source: "ansible.cfg", destination: "/home/vagrant/.ansible.cfg"
    config.vm.network "private_network", ip: "10.0.0.2"
    config.vm.host_name = "solar-dev"

    config.vm.provider :virtualbox do |v|
      v.customize ["modifyvm", :id, "--memory", 1024]
      v.name = "solar-dev"
    end
  end

  SLAVES_COUNT.times do |i|
    index = i + 1
    ip_index = i + 3
    config.vm.define "solar-dev#{index}" do |config|
      config.vm.provision "shell", inline: init_script, privileged: true
      config.vm.provision "shell", inline: slave_script, privileged: true
      config.vm.provision "shell", inline: slave_celery, privileged: true
      config.vm.network "private_network", ip: "10.0.0.#{ip_index}"
      config.vm.host_name = "solar-dev#{index}"

      config.vm.provider :virtualbox do |v|
        v.customize ["modifyvm", :id, "--memory", 1024]
        v.name = "solar-dev#{index}"
      end
    end
  end

end
