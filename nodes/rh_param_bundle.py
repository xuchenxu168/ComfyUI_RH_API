"""
RH_ParamBundle Node - Bundle multiple parameter sets for batch execution.
"""

class RH_ParamBundle:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {},
            "optional": {
                "params_1": ("RH_PARAMS",),
                "params_2": ("RH_PARAMS",),
                "params_3": ("RH_PARAMS",),
                "params_4": ("RH_PARAMS",),
                "params_5": ("RH_PARAMS",),
                "params_6": ("RH_PARAMS",),
                "params_7": ("RH_PARAMS",),
                "params_8": ("RH_PARAMS",),
                "params_9": ("RH_PARAMS",),
                "params_10": ("RH_PARAMS",),
            }
        }

    RETURN_TYPES = ("RH_PARAM_BUNDLE",)
    FUNCTION = "bundle"
    CATEGORY = "Ken-Chen/RH-API"

    def bundle(self, params_1=None, params_2=None, params_3=None, params_4=None, params_5=None,
               params_6=None, params_7=None, params_8=None, params_9=None, params_10=None):
        batch_bundle = []

        # Collect all non-None parameter sets
        param_inputs = [params_1, params_2, params_3, params_4, params_5,
                       params_6, params_7, params_8, params_9, params_10]

        for i, param_set in enumerate(param_inputs, 1):
            if param_set is not None:
                if isinstance(param_set, list):
                    batch_bundle.append(param_set)
                else:
                    # This should not happen if connected to RH_Param, but as a safeguard
                    print(f"[Warning] RH_ParamBundle received a non-list input for 'params_{i}'. Wrapping it.")
                    batch_bundle.append([param_set])

        if not batch_bundle:
            print("[Warning] RH_ParamBundle: No parameter sets received.")
            return ([],)

        print(f"[Info] RH_ParamBundle: Bundled {len(batch_bundle)} parameter sets.")
        return (batch_bundle,)

