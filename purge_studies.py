import requests

def get_studies(url):
    """Perform an HTTP GET request to retrieve the list of studies."""
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad status codes
    return response.json()

def delete_study(url, study_id):
    """Perform an HTTP DELETE request to delete a study by its ID."""
    delete_url = f"{url}/{study_id}"
    response = requests.delete(delete_url)
    response.raise_for_status()  # Raise an error for bad status codes
    print(f"Deleted study with ID: {study_id}")

def main():
    base_url = "https://pacs.radassist.ai/studies"

    try:
        # Get the list of studies
        studies = get_studies(base_url)
        print(f"Retrieved {len(studies)} studies.")

        # Delete each study in the list
        for study in studies:
            print("Deleting Study ::", study)
            delete_study(base_url, study)
            # study_id = study.get('id')  # Adjust the key if the ID is stored under a different key
            # if study_id:
            #     delete_study(base_url, study_id)

    except requests.RequestException as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
