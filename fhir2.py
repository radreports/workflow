from fhirclient.models.annotation import Annotation

note1 = {
      "text": "Modality:"
    }
note2 = {
    "text": "body_part:"
}
Note = []
Note.append(note1)
Note.append(note2)
annot = Annotation(note1)
