class OpenshiftTools:

    def __init__(self):
        pass

    # ============================================================================== #
    #   Functions to format json file in order to push to openshift API              #
    #   session to create all format functions of this class                         #
    # ============================================================================== #
    #
    def insert_environment(self, dc, overwrite, environment, json_data):
        """
            Method to insert all new Openshift environment and update all environment
            that already exists.

        :param dc:              Specific name of the deployment-config.
        :param overwrite:       Variable to control if will be overwriting existing variables (True/False).
        :param environment:     List of variables to be add into a DeploymentConfig.
        :param json_data:       Variable with all json formatted and ready to push to API/OAPI.
        :return:                Return the gathered json from API/OAPI with new envs inside.
        """

        if dc is None or json_data is None or environment is None:
            print("==> Error: DeploymentConfig, json_data or Environment not informed, exiting...")
            exit(1)
        else:
            # List with all new environment to be add in our DC
            lista_variaveis = []
            lista_remover = []

            for item in environment.split(','):
                env = item.split('=', maxsplit=1)

                # Check nevironment to remove and add to a special list
                if '-' in env[0]:
                    lista_remover.append(env[0].replace('-', ''))
                    continue
                else:
                    if env[1] is not None:
                        lista_variaveis.append(
                            {
                                'name': '{0}'.format(env[0]),
                                'value': '{0}'.format(env[1])
                            })
                    else:
                        lista_variaveis.append(
                            {
                                'name': '{0}'.format(env[0])
                            })
                # Fim do IF
            # List to control and ensures no duplications in our DC
            list_not_add = []

            for containers in json_data['spec']['template']['spec']['containers']:
                if dc in containers['name']:
                    if overwrite:
                        for env in containers['env']:
                            for new_env in lista_variaveis:
                                if env['name'] == new_env['name']:
                                    env['value'] = new_env['value']
                                    list_not_add.append(new_env['name'])
                                    pass
                                pass
                            pass
                        pass
                        for item in lista_variaveis:
                            if item['name'] not in list_not_add:
                                containers.setdefault('env', []).append(item)
                                pass
                            pass
                        pass
                    else:
                        for item in lista_variaveis:
                            containers['env'].append(item)
                            pass
                        pass
                    pass
                else:
                    for item in lista_variaveis:
                        containers.setdefault('env', []).append(item)
                        pass
                    pass
                pass

            # Remove envs listed before
            if lista_remover is not None:
                for containers in json_data['spec']['template']['spec']['containers']:
                    containers['env'] = [dic for dic in containers['env'] if dic['name'] not in lista_remover]
            # End of IF

            # Return data formated and ready for OAPI/API
            return json_data

        # Impossible to get here... But keep it for curiosity rs
        exit(1)

    #
    def insert_resourcelimits(self, dc, cpu_type, cpu_req, cpu_lim, mem_type, mem_req, mem_lim, json_data):
        """
            Method to insert a resource-limits to a DeploymentConfig inside a project on Openshift.

        :param dc:              Specific name of the deployment-config.
        :param cpu_type:        Variable that shows and control the type(C,mC) imputed.
        :param cpu_req:         Variable with the CPU requirement (lowest value) for it.
        :param cpu_lim:         Variable with the CPU maximum usage (highest value) for it.
        :param mem_type:        Variable that shows and control the type(M,G) imputed.
        :param mem_req:         Variable with the MEM requirement (lowest value) for it.
        :param mem_lim:         Variable with the MEM maximum usage (highest value) for it.
        :param json_data:       Variable with all json formatted and ready to push to API/OAPI.
        :return:                Return the gathered json from API/OAPI with new envs inside.
        """

        if dc is None or json_data is None:
            print("==> Error: DeploymentConfig or json_data not informed, exiting...")
            exit(1)
        else:
            for containers in json_data['spec']['template']['spec']['containers']:
                #
                # Check if key exist.
                if not containers['resources'].get('requests'):
                    containers['resources'].setdefault('requests', {})

                # Check if key exist.
                if not containers['resources'].get('limits'):
                    containers['resources'].setdefault('limits', {})

                # ------------------------------------------------ #

                # Define resource requests. if has some value
                if cpu_req is not None:
                    containers['resources'].setdefault('requests', {'cpu', cpu_req})

                if mem_req is not None:
                    containers['resources'].setdefault('requests', {'mem', mem_req})

                # ------------------------------------------------ #

                # Define resource limits, if has some value
                if cpu_lim is not None:
                    containers['resouces'].setdefault('limits', {'cpu': cpu_lim})

                if mem_lim is not None:
                    containers['resouces'].setdefault('limits', {'mem': mem_lim})

                # ------------------------------------------------ #

        return json_data

    def insert_route(self, service, tls_enabled, type_tls, json_data):
        """
            Method to format/insert all values passed into the json.
            It check's if the key exists or not to insert or to create and
            then insert into.

        :param service:     Name of the service this route will refer to.
        :param tls_enabled: Enable/Disable TLS in this route.
        :param type_tls:    If tlsEnabled, set the TLS type. If not, even touch it.
        :param json_data:   Variable with all json formatted and ready to push to API/OAPI.
        :return:            Return the gathered json from API/OAPI with the route values inside.
        """

        # Check TLS usage.
        # if not set True, then delete de TLS field
        if tls_enabled:
            json_data['spec'].setdefault('tls', {'termination': str(type_tls)})
        else:
            json_data['spec']['tls'].delete()

        # Update route service
        json_data['spec']['to'].setdefault('name', str(service))

        #
        return json_data

    def insert_probe_liveness(self, path, init_delay, timeout, json_data):
        """
            Method to insert/edit a LivenessProbe from a specified DeploymentConfig

        :param path:            Path for liveness to probe for.
        :param init_delay:      Initial delay (from creation) to start probing.
        :param timeout:         Time to consider it a TimeOut in probing.
        :param json_data:       Variable with all json formatted and ready to push to API/OAPI.
        :return:                Return the gathered json from API/OAPI with the route values inside.
        """

        for containers in json_data['spec']['template']['spec']['containers']:
            containers.setdefault('livenessProbe', {
                'failureThreshold': 3,
                'httpGet': {
                    'path': path,
                    'port': 8080,
                    'scheme': 'HTTP'
                },
                'initialDelaySeconds': init_delay,
                'periodSeconds': 10,
                'successThreshold': 1,
                'timeoutSeconds': timeout
            })
        return json_data

    def insert_probe_readiness(self, path, init_delay, timeout, json_data):
        """
            Method to insert/edit a ReadinessProbe from a specified DeploymentConfig

        :param path:            Path for readiness to probe for.
        :param init_delay:      Initial delay (from creation) to start probing.
        :param timeout:         Time to consider it a TimeOut in probing.
        :param json_data:       Variable with all json formatted and ready to push to API/OAPI.
        :return:                Return the gathered json from API/OAPI with the route values inside.
        """
        for containers in json_data['spec']['template']['spec']['containers']:
            containers.setdefault('readinessProbe', {
                'failureThreshold': 3,
                'httpGet': {
                    'path': path,
                    'port': 8080,
                    'scheme': 'HTTP'
                },
                'initialDelaySeconds': int(init_delay),
                'periodSeconds': 10,
                'successThreshold': 1,
                'timeoutSeconds': int(timeout)
            })
        return json_data

    def insert_autoscale(self, app, scale_minimum, scale_maximum, cpu_usage, json_data):
        """
            Method to insert/edit a scale from a specified DeploymentConfig

        :param dc:                  Name of the deploymentconfig (Used only to create new autoscale)
        :param scale_minimum:       Minimum scale required for this deploymentconfig (default 1)
        :param scale_maximum:       Maximum scale required for this deploymentconfig (defalt 1)
        :param cpu_usage:           CPU usage requested to scale a deploymentconfig (default 80%)
        :param json_data:           Variable with all json formatted and ready to push to API/OAPI.
        :return:                    Return the gathered json from API/OAPI with the scale values.
        """
        # ================================================== #
        # Validation process (Default values)
        if int(scale_minimum) <= 1 or scale_minimum is None:
            scale_minimum = 1

        if int(scale_maximum) <= 1 or scale_maximum is None:
            scale_maximum = 1

        if int(cpu_usage) <= 1 or cpu_usage is None:
            cpu_usage = 80

        # ================================================== #
        if json_data is not None and json_data['kind'] == 'HorizontalPodAutoscaler':
            # In those case (autoscale already exists), there's no need to use the
            # 'app' parameter.
            ####
            if json_data['spec'].get('minReplicas'):
                json_data['spec']['minReplicas'] = scale_minimum
            else:
                json_data['spec'].setdefault('minReplicas', scale_minimum)
            ####
            if json_data['spec'].get('maxReplicas'):
                json_data['spec']['maxReplicas'] = scale_maximum
            else:
                json_data['spec'].setdefault('maxReplicas', scale_maximum)
            ####
            if json_data['spec'].get('targetCPUUtilizationPercentage'):
                json_data['spec']['targetCPUUtilizationPercentage'] = cpu_usage
            else:
                json_data['spec'].setdefault('targetCPUUtilizationPercentage', cpu_usage)
            ####
            return json_data
        else:
            if app is None:
                print("==> Error: No deploymentconfig name informed to create autoscale")
                exit(1)

            json_data = {
                "kind": "HorizontalPodAutoscaler",
                "apiVersion": "autoscaling/v1",
                "metadata": {
                    "name": "{0}".format(app),
                    "labels": {"app_name": "{0}".format(app)}
                },
                "spec": {
                    "scaleTargetRef": {
                        "kind": "DeploymentConfig",
                        "name": "{0}".format(app),
                        "apiVersion": "extensions/v1beta1"
                },
                "minReplicas": "{0}".format(scale_minimum),
                "maxReplicas": "{0}".format(scale_maximum),
                "targetCPUUtilizationPercentage": "{0}".format(cpu_usage)
                }}
            return json_data

    def deploy_rollback(self, dc, version):
        """
            Method to return default structure to trigger a deploy rollback.

        :param dc:              Name of the deploymentconfig to rollback.
        :param version:         Version of the deploymentconfig to rollback.
        :return:                Return default structure to trigger deploy rollback.
        """
        # Controler
        validator = 0

        #
        if dc is None or len(dc) < 3:
            print("Erro: nome do deploymentconfig e invalido.")
            validator += 1

        #
        if version is None or version < 1:
            print("Erro: nome do deploymentconfig e invalido.")
            validator += 1

        #
        if validator is not 0:
            return False
        else:
            #
            data = {
                "kind": "DeploymentConfigRollback",
                "apiVersion": "v1",
                "name": "{0}".format(dc),
                "spec": {
                    "from": {},
                    "revision": "{0}".format(version),
                    "includeTriggers": False,
                    "includeTemplate": True,
                    "includeReplicationMeta": False,
                    "includeStrategy": False
                }
            }
            return data
        # End of IF
    # End of function

    def deploy_latest(self, dc):
        """
            Method to return default structure to trigger a new deploy.

        :param dc:          Name of the deploymentconfig.
        :return:            Return default structure to deploy.
        """
        #
        if dc is None or len(dc) < 3:
            print("Erro: nome do deploymentconfig e invalido.")
            return 1
        #
        data = {
            "kind": "DeploymentRequest",
            "apiVersion":"v1",
            "name":"{0}".format(dc),
            "latest": True,
            "force": True
        }
        return data
    # End of function
