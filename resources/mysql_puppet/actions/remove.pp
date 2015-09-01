$package_name        = $resource['input']['package_name']['value']
$client_package_name = $resource['input']['client_package_name']['value']

class {'mysql':
  service_enabled => false,
  package_ensure  => 'absent',
  package_name    => $package_name,
}

class {'mysql::client':
  package_ensure => 'absent',
  package_name   => $client_package_name,
}