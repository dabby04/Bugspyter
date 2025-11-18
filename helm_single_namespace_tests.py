#!/usr/bin/env python
# coding: utf-8

# # Example Seldon Core Deployments using Helm
# <img src="images/deploy-graph.png" alt="predictor with canary" title="ml graph"/>

# ## Prerequistes
# You will need
#  - [Git clone of Seldon Core](https://github.com/SeldonIO/seldon-core)
#  - A running Kubernetes cluster with kubectl authenticated
#  - [python grpc tools](https://grpc.io/docs/quickstart/python.html)
#  - [Helm client](https://helm.sh/)

# ### Creating a Kubernetes Cluster
# 
# Follow the [Kubernetes documentation to create a cluster](https://kubernetes.io/docs/setup/).
# 
# Once created ensure ```kubectl``` is authenticated against the running cluster.

# # Setup

# In[ ]:


get_ipython().system('kubectl create namespace seldon')


# In[ ]:


get_ipython().system('kubectl config set-context $(kubectl config current-context) --namespace=seldon')


# In[ ]:


get_ipython().system('kubectl create clusterrolebinding kube-system-cluster-admin --clusterrole=cluster-admin --serviceaccount=kube-system:default')


# # Install Helm

# In[ ]:


get_ipython().system('kubectl -n kube-system create sa tiller')
get_ipython().system('kubectl create clusterrolebinding tiller --clusterrole cluster-admin --serviceaccount=kube-system:tiller')
get_ipython().system('helm init --service-account tiller')


# In[ ]:


get_ipython().system('kubectl rollout status deploy/tiller-deploy -n kube-system')


# ## Start seldon-core

# In[ ]:


get_ipython().system('helm install ../../helm-charts/seldon-core-crd --name seldon-core-crd --set usage_metrics.enabled=true')


# In[ ]:


get_ipython().system('helm install ../../helm-charts/seldon-core --name seldon-core --namespace seldon  --set ambassador.enabled=true --set ambassador.env.AMBASSADOR_SINGLE_NAMESPACE=true')


# In[ ]:


get_ipython().system('kubectl rollout status deploy/seldon-core-seldon-cluster-manager')
get_ipython().system('kubectl rollout status deploy/seldon-core-seldon-apiserver')
get_ipython().system('kubectl rollout status deploy/seldon-core-ambassador')


# ## Set up REST and gRPC methods
# 
# **Ensure you port forward ambassador and API gateway**:
# 
# ```
# kubectl port-forward $(kubectl get pods -n seldon -l app.kubernetes.io/name=ambassador -o jsonpath='{.items[0].metadata.name}') -n seldon 8003:8080
# ```
# 
# ```
# kubectl port-forward $(kubectl get pods -n seldon -l app=seldon-apiserver-container-app -o jsonpath='{.items[0].metadata.name}') -n seldon 8002:8080
# ```
# 
# ```
# kubectl port-forward $(kubectl get pods -n seldon -l app=seldon-apiserver-container-app -o jsonpath='{.items[0].metadata.name}') -n seldon 8004:5000
# ```

# ## Serve Single Model

# In[ ]:


get_ipython().system('helm install ../../helm-charts/seldon-single-model --name mymodel --set model.image.name=seldonio/mock_classifier_rest:1.2 --set oauth.key=oauth-key --set oauth.secret=oauth-secret')


# In[ ]:


get_ipython().system('helm template ../../helm-charts/seldon-single-model --name mymodel --set oauth.key=oauth-key --set oauth.secret=oauth-secret | pygmentize -l json')


# In[ ]:


get_ipython().system('kubectl rollout status deploy/mymodel-mymodel-951ca8b')


# ### Get predictions

# In[2]:


from seldon_core.seldon_client import SeldonClient
sc = SeldonClient(deployment_name="mymodel",namespace="seldon",oauth_key="oauth-key",oauth_secret="oauth-secret")


# #### REST Request

# In[3]:


p = sc.predict(gateway="seldon",transport="rest")
print(p)


# In[ ]:


p = sc.predict(gateway="ambassador",transport="rest")
print(p)


# #### gRPC Request

# In[ ]:


p = sc.predict(gateway="ambassador",transport="grpc")
print(p)


# In[ ]:


p = sc.predict(gateway="seldon",transport="grpc")
print(p)


# ## Test Feedback

# In[ ]:


p = sc.predict(gateway="seldon",transport="rest")
f = sc.feedback(p.request,p.response,1.0,gateway="seldon",transport="rest")
print(f)


# In[ ]:


p = sc.predict(gateway="ambassador",transport="rest")
f = sc.feedback(p.request,p.response,1.0,gateway="ambassador",transport="rest")
print(f)


# ### gRPC

# In[ ]:


p = sc.predict(gateway="ambassador",transport="grpc")
f = sc.feedback(p.request,p.response,1.0,gateway="ambassador",transport="grpc")
print(f)


# In[ ]:


p = sc.predict(gateway="seldon",transport="grpc")
f = sc.feedback(p.request,p.response,1.0,gateway="seldon",transport="grpc")
print(f)


# In[ ]:


get_ipython().system('helm delete mymodel --purge')


# ## Serve AB Test

# In[ ]:


get_ipython().system('helm install ../../helm-charts/seldon-abtest --name myabtest --set oauth.key=oauth-key --set oauth.secret=oauth-secret')


# In[ ]:


get_ipython().system('kubectl rollout status deploy/myabtest-abtest-41de5b8')
get_ipython().system('kubectl rollout status deploy/myabtest-abtest-df66c5c')


# ### Get predictions

# In[ ]:


sc = SeldonClient(deployment_name="myabtest",namespace="seldon",oauth_key="oauth-key",oauth_secret="oauth-secret")


# In[ ]:


r = sc.predict(gateway="seldon",transport="rest")
print(r)


# In[ ]:


r = sc.predict(gateway="ambassador",transport="rest")
print(r)


# #### gRPC Request

# In[ ]:


r = sc.predict(gateway="ambassador",transport="grpc")
print(r)


# In[ ]:


r = sc.predict(gateway="seldon",transport="grpc")
print(r)


# In[ ]:


get_ipython().system('helm delete myabtest --purge')


# ## Serve Multi-Armed Bandit

# In[ ]:


get_ipython().system('helm install ../../helm-charts/seldon-mab --name mymab --set modela.image.name=seldonio/mock_classifier_rest:1.2 --set modelb.image.name=seldonio/mock_classifier_rest:1.2 --set oauth.key=oauth-key --set oauth.secret=oauth-secret')


# In[ ]:


get_ipython().system('kubectl rollout status deploy/mymab-abtest-295a20e')
get_ipython().system('kubectl rollout status deploy/mymab-abtest-b8038b2')
get_ipython().system('kubectl rollout status deploy/mymab-abtest-5724b8a')


# ### Get predictions

# In[ ]:


sc = SeldonClient(deployment_name="mymab",namespace="seldon",oauth_key="oauth-key",oauth_secret="oauth-secret")


# In[ ]:


r = sc.predict(gateway="seldon",transport="rest")
print(r)


# In[ ]:


r = sc.predict(gateway="ambassador",transport="rest")
print(r)


# #### gRPC Request

# In[ ]:


r = sc.predict(gateway="ambassador",transport="grpc")
print(r)


# In[ ]:


r = sc.predict(gateway="seldon",transport="grpc")
print(r)


# In[ ]:


get_ipython().system('helm delete mymab --purge')


# In[ ]:




