k8s_yaml(kustomize('kubernetes/tilt'))

k8s_resource(
  objects=['ledger-app-unum:namespace'],
  new_name='namespace'
)

local_resource(
    name='config', resource_deps=['namespace'],
    cmd='kubectx docker-desktop && kubectl -n ledger-app-unum create configmap config --from-file config/ --dry-run=client -o yaml | kubectl apply -f -'
)

local_resource(
    name='secret', resource_deps=['namespace'],
    cmd='kubectx docker-desktop && kubectl -n ledger-app-unum create secret generic secret --from-file secret/ --dry-run=client -o yaml | kubectl apply -f -'
)

# api

docker_build('unum-apps-ledger-api', './api')
k8s_resource('api', port_forwards=['14465:80', '14433:5678'], resource_deps=['secret'])

# gui

docker_build('unum-apps-ledger-gui', './gui')
k8s_resource('gui', port_forwards=['4465:80'], resource_deps=['api'])

# daemon

docker_build('unum-apps-ledger-daemon', './daemon')
k8s_resource('daemon', port_forwards=['24433:5678'], resource_deps=['api'])

# cron

docker_build('unum-apps-ledger-cron', './cron')
k8s_resource('cron', port_forwards=['34433:5678'], resource_deps=['secret'])

# redis

k8s_resource('redis', port_forwards=['24465:6379'])
