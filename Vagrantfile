# -*- mode: ruby -*-
# vi: set ft=ruby :

require 'yaml'

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

# configs, custom updates _defaults
defaults_cfg = YAML.load_file('vagrant-settings.yml_defaults')
if File.exist?('vagrant-settings.yml')
  custom_cfg = YAML.load_file('vagrant-settings.yml')
  cfg = defaults_cfg.merge(custom_cfg)
else
  cfg = defaults_cfg
end

SLAVES_COUNT = cfg["slaves_count"]
SLAVES_RAM = cfg["slaves_ram"]
SLAVES_CPU = cfg["slaves_cpu"]
SLAVES_IPS = cfg["slaves_ips"]
MASTER_RAM = cfg["master_ram"]
MASTER_CPU = cfg["master_cpu"]
MASTER_IPS = cfg["master_ips"]

def ansible_playbook_command(filename, args=[])
  "ansible-playbook -v -i \"localhost,\" -c local /vagrant/bootstrap/playbooks/#{filename} #{args.join ' '}"
end

solar_script = ansible_playbook_command("solar.yml")

slave_script = ansible_playbook_command("custom-configs.yml", ["-e", "master_ip=10.0.0.2"])

master_celery = ansible_playbook_command("celery.yml", ["--skip-tags", "slave"])

slave_celery = ansible_playbook_command("celery.yml", ["--skip-tags", "master"])

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

  config.vm.define "solar-dev", primary: true do |config|
      #config.vm.box = "deb/jessie-amd64"
      #config.vm.box = "rustyrobot/deb-jessie-amd64"
      #config.vm.box = "ubuntu/trusty64"
      config.vm.box = "cgenie/solar-master"

    config.vm.provision "shell", inline: solar_script, privileged: true
    config.vm.provision "shell", inline: master_celery, privileged: true
    config.vm.provision "file", source: "~/.vagrant.d/insecure_private_key", destination: "/vagrant/tmp/keys/ssh_private"
    config.vm.provision "file", source: "ansible.cfg", destination: "/home/vagrant/.ansible.cfg"
    MASTER_IPS.each do |ip|
      config.vm.network "private_network", ip: "#{ip}"
    end
    config.vm.host_name = "solar-dev"

    config.vm.provider :virtualbox do |v|
      v.customize [
        "modifyvm", :id,
        "--memory", MASTER_RAM,
        "--cpus", MASTER_CPU,
        "--paravirtprovider", "kvm" # for linux guest
      ]
      v.name = "solar-dev"
    end
  end

  SLAVES_COUNT.times do |i|
    index = i + 1
    ip_index = i + 3
    config.vm.define "solar-dev#{index}" do |config|
      # standard box with all stuff preinstalled
      config.vm.box = "cgenie/solar-master"

      config.vm.provision "shell", inline: slave_script, privileged: true
      config.vm.provision "shell", inline: solar_script, privileged: true
      config.vm.provision "shell", inline: slave_celery, privileged: true
      SLAVES_IPS.each do |ip|
        config.vm.network "private_network", ip: "#{ip}#{ip_index}"
      end
      config.vm.host_name = "solar-dev#{index}"

      config.vm.provider :virtualbox do |v|
        v.customize [
            "modifyvm", :id,
            "--memory", SLAVES_RAM,
            "--cpus", SLAVES_CPU,
            "--paravirtprovider", "kvm" # for linux guest
        ]
        v.name = "solar-dev#{index}"
      end
    end
  end

end
