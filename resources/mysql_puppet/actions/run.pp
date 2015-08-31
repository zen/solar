$resource = hiera($::resource_name)

$ip = $resource['input']['ip']['value']

$config_file              = $resource['input']['config_file']['value']
$includedir               = $resource['input']['includedir']['value']
$install_options          = $resource['input']['install_options']['value']
$install_secret_file      = $resource['input']['install_secret_file']['value']
$manage_config_file       = $resource['input']['manage_config_file']['value']
$override_options         = $resource['input']['override_options']['value']
$package_ensure           = $resource['input']['package_ensure']['value']
$package_name             = $resource['input']['package_name']['value']
$purge_conf_dir           = $resource['input']['purge_conf_dir']['value']
$remove_default_accounts  = $resource['input']['remove_default_accounts']['value']
$restart                  = $resource['input']['restart']['value']
$root_group               = $resource['input']['root_group']['value']
$mysql_group              = $resource['input']['mysql_group']['value']
$root_password            = $resource['input']['root_password']['value']
$service_name             = $resource['input']['service_name']['value']
$service_provider         = $resource['input']['service_provider']['value']
$create_root_user         = $resource['input']['create_root_user']['value']
$create_root_my_cnf       = $resource['input']['create_root_my_cnf']['value']
$users                    = $resource['input']['users']['value']
$grants                   = $resource['input']['grants']['value']
$databases                = $resource['input']['databases']['value']

$client_bindings_enable  = $resource['input']['client_bindings_enable']['value']
$client_package_name     = $resource['input']['client_package_name']['value']

class {'mysql':
  server_package_manage    => true,
  server_service_manage    => true,
  server_service_enabled   => true,
  config_file              => $config_file,
  includedir               => $includedir,
  install_options          => $install_options,
  install_secret_file      => $install_secret_file,
  manage_config_file       => $manage_config_file,
  override_options         => $override_options,
  package_ensure           => $package_ensure,
  package_name             => $package_name,
  purge_conf_dir           => $purge_conf_dir,
  remove_default_accounts  => $remove_default_accounts,
  restart                  => $restart,
  root_group               => $root_group,
  mysql_group              => $mysql_group,
  root_password            => $root_password,
  service_name             => $service_name,
  service_provider         => $service_provider,
  create_root_user         => $create_root_user,
  create_root_my_cnf       => $create_root_my_cnf,
  users                    => $users,
  grants                   => $grants,
  databases                => $databases,
} ->

class {'mysql::client':
  bindings_enable => $client_bindings_enable,
  package_ensure  => true,
  package_manage  => true,
  package_name    => $client_package_name,
}