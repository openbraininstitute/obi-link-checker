
def get_dynamic_pages(base_url, lab_id, project_id):
    return [
        f"{base_url}",
        f"{base_url}/about",
        f"{base_url}/mission",
        f"{base_url}/news",
        f"{base_url}/pricing",
        f"{base_url}/team",
        f"{base_url}/resources",
        f"{base_url}/terms",
        f"{base_url}/privacy",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/overview",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/projects",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/home",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/team",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/library",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/admin",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/notebooks",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/notebooks/member",
        f"{base_url}/app/virtual-lab/lab/{lab_id}"
        f"/project/{project_id}/explore/interactive/experimental/morphology?brainRegion=http"
        f"%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/"
        f"{project_id}/explore/interactive/experimental/electrophysiology?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/"
        f"{project_id}/explore/interactive/experimental/neuron-density?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/"
        f"{project_id}/explore/interactive/experimental/bouton-density?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/"
        f"{project_id}/explore/interactive/experimental/synapse-per-connection?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/"
        f"{project_id}/explore/interactive?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/"
        f"{project_id}/explore/interactive/model/e-model?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi"
        f"%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/"
        f"{project_id}/explore/interactive/model/me-model?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/"
        f"project/{project_id}/explore/interactive/model/synaptome?brainRegion=http%253A"
        f"%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567"
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/build",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/build/me-model/new",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/build/synaptome/new",
        f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/simulate",
    ]

