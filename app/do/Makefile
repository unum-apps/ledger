CLUSTER="do-{{ unum }}-unum"
NAMESPACE="ledger"
SERVICE="gui"
LOCAL_PORT=7601
.PHONY: tfenv init remote install uninstall

tfenv:
	tfenv use 1.10.5

init: tfenv
	terraform init

remote:
	@open "http://localhost:${LOCAL_PORT}"
	kubectl --context=${CLUSTER} port-forward -n ${NAMESPACE} service/${SERVICE} ${LOCAL_PORT}:http

install: init
	terraform apply

uninstall: init
	terraform destroy
