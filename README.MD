This init-container is use for manually update endpoint target. 
Normally you should use Kubernetes service with selector to let Kubernetes manage endpoint.

But if your use case is need to use readiness probe to determine is pod ready for service, 
and whatever is it ready or not, you want reach the pod by another service. Then this init-container is fit for you.

In my case I'm using cluster of [vault], when it is unsealed, auto join to service, otherwise not join the service. 
This use readiness probe to achieve. But I need a way to reach individual vault pod to perform unseal, 
and I can't found a way to make service ignore readiness probe result. 
So I need to remove selector from individual vault, and manually config endpoint target by this init-container.

In [register_to_endpoint.py], I hardcoded vault port, please change to your target. 
I may update it to input from args later.


[vault]: https://www.vaultproject.io/
[register_to_endpoint.py]: https://github.com/alantang888/Kubernetes_Init_Container_For_Endpoint_Update/blob/master/register_to_endpoint.py