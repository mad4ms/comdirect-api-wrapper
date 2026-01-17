from dataclasses import dataclass
from .common import IsoDate


@dataclass(frozen=True)
class Document:
    document_id: str
    name: str
    mime_type: str
    created: IsoDate

    @classmethod
    def from_api(cls, data):
        return cls(
            document_id=data["documentId"],
            name=data["name"],
            mime_type=data["mimeType"],
            created=IsoDate.from_string(data["dateCreation"]),
        )
