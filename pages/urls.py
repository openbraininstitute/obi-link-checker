import logging

def get_dynamic_pages(base_url, lab_id, project_id):

    if "production.org" in base_url:
        logging.info("⚠️ Base URL is production.org, but it will redirect to openbluebrain.com.")
        print("⚠️ Base URL is production.org, but it will redirect to openbluebrain.com.")

        base_url = "https://openbluebrain.com/app"
        logging.info(f"🔄 Updating base_url to: {base_url}")
        print(f"🔄 Updating base_url to: {base_url}")

    return [
        f"{base_url}/virtual-lab/lab/{lab_id}/project/{project_id}/home",
        f"{base_url}/virtual-lab/lab/{lab_id}/project/{project_id}/explore/interactive/experimental/morphology"
        f"?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        f"{base_url}/virtual-lab/lab/{lab_id}/project/{project_id}/build",
    ]

    # return [
        # f"{base_url}/virtual-lab/lab/{lab_id}",
        # f"{base_url}/virtual-lab/lab/{lab_id}/project/{project_id}/",
        # f"{base_url}/virtual-lab/lab/{lab_id}/project/{project_id}/home/explore",
        # f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/explore/interactive?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
        # f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/build",
    # ]

    # return [
    #     f"{base_url}/app/virtual-lab/lab/{lab_id}",
    #     f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/",
    #     f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/home/explore",
    #     f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/explore/interactive?brainRegion=http%253A%252F%252Fapi.brain-map.org%252Fapi%252Fv2%252Fdata%252FStructure%252F567",
    #     f"{base_url}/app/virtual-lab/lab/{lab_id}/project/{project_id}/build",
    # ]
