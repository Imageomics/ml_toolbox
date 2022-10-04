from argparse import ArgumentParser

def parse_butterfly_labels(path: str, use_specimen_as_key: False) -> dict:
    """
    Inputs: 
        path: path to .csv file of labels for the butterfly data in the Cuthil dataset.
        use_specimen_as_key: set to true if desire to have the specimen id as key instead of image id

    This function will parse a .csv file into a Python dictionary containing the image's id
    and a dictionary for each image's attributes/features.

    The information currently collected per image is as follows:
    Image ID, Specimen ID, file name, view side of butterfly, species name, subspecies name
    """
    assert path.split(".")[-1].lower() == 'csv', "path must be a .csv file"

    labels = {}
    with open(path, 'r') as f:
        rows = f.readlines()
        for i, row in enumerate(rows):
            if i == 0: continue # Skip the header row
            img_id, specimen_id, fname, view, species, subspecies = row.split(',')[:6]
            key = specimen_id if use_specimen_as_key else img_id
            labels[key] = {
                "specimen_id" : specimen_id,
                "filename" : fname,
                "view" : 'unknown' if use_specimen_as_key else view,
                "species" : species,
                "subspecies" : subspecies
            }

    return labels

if __name__ == "__main__":
    """
    Use main for testing
    """
    parser = ArgumentParser()
    parser.add_argument('--path_to_labels', type=str, default='data/Cuthill_GoldStandard/Hoyal_Cuthill_GoldStandard_metadata_cleaned.csv')
    args = parser.parse_args()

    lbls = parse_butterfly_labels(args.path_to_labels)
    print(lbls)

