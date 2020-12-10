# cluster
helm install mygraph https://github.com/neo4j-contrib/neo4j-helm/releases/download/4.2.0-1/neo4j-4.2.0-1.tgz --set acceptLicenseAgreement=yes --set neo4jPassword=dp8cz8SEnfU7

# standalone
$ helm install mygraph https://github.com/neo4j-contrib/neo4j-helm/releases/download/4.2.0-1/neo4j-4.2.0-1.tgz --set core.standalone=true --set acceptLicenseAgreement=yes --set neo4jPassword=dp8cz8SEnfU7



NAME: mygraph
LAST DEPLOYED: Thu Dec 10 23:01:56 2020
NAMESPACE: default
STATUS: deployed
REVISION: 1
NOTES:
Your cluster is now being deployed, and may take up to 5 minutes to become available.
If you'd like to track status and wait on your rollout to complete, run:

$ kubectl rollout status \
    --namespace default \
    StatefulSet/mygraph-neo4j-core \
    --watch

You can inspect your logs containers like so:

We can see the content of the logs by running the following command:

$ kubectl logs --namespace default -l \
    "app.kubernetes.io/instance=mygraph,app.kubernetes.io/name=neo4j,app.kubernetes.io/component=core"

We can now run a query to find the topology of the cluster.

export NEO4J_PASSWORD=$(kubectl get secrets mygraph-neo4j-secrets --namespace default -o jsonpath='{.data.neo4j-password}' | base64 -d)
kubectl run -it --rm cypher-shell \
    --image=neo4j:4.2.0-enterprise \
    --restart=Never \
    --namespace default \
    --command -- ./bin/cypher-shell -u neo4j -p "$NEO4J_PASSWORD" -a neo4j://mygraph-neo4j.default.svc.cluster.local "call dbms.routing.getRoutingTable({}, 'system');"

This will print out the addresses of the members of the cluster.

Note:
You'll need to substitute <password> with the password you set when installing the Helm package.
If you didn't set a password, one will be auto generated.
You can find the base64 encoded version of the password by running the following command:

kubectl get secrets mygraph-neo4j-secrets -o yaml --namespace default
