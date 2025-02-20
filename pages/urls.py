
def get_dynamic_pages(base_url, lab_id, project_id):
    return [
        f"{base_url}/virtual-lab/lab/{lab_id}/project/{project_id}/home",
        f"{base_url}/virtual-lab/lab/{lab_id}/project/{project_id}/explore/interactive/experimental/morphology?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/virtual-lab/lab/{lab_id}/project/{project_id}/build",
    ]

