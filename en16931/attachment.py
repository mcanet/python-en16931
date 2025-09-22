"""
Class for representing file attachments in EN16931 documents.
"""
import base64
import mimetypes
import os


class Attachment:
    """EN16931 Attachment class.

    This class represents file attachments that can be embedded
    in invoices and credit notes according to EN16931 standard.

    Attachments are embedded as base64-encoded binary objects
    within the XML document.

    Example usage:

    >>> attachment = Attachment()
    >>> attachment.load_from_file('/path/to/document.pdf')
    >>> attachment.description = "Invoice supporting documentation"

    Or create from data directly:

    >>> attachment = Attachment(
    ...     filename="contract.pdf",
    ...     mime_type="application/pdf", 
    ...     data=pdf_bytes,
    ...     description="Contract documentation"
    ... )
    """

    def __init__(self, filename=None, mime_type=None, data=None, 
                 description=None, document_type=None):
        """Initialize an Attachment.

        Parameters
        ----------
        filename: string (optional)
            The original filename of the attachment.

        mime_type: string (optional)
            MIME type of the file (e.g., 'application/pdf').

        data: bytes (optional)
            Binary data of the file.

        description: string (optional)
            Human-readable description of the attachment.

        document_type: string (optional)
            Document type classification (e.g., 'Contract', 'Invoice').
        """
        self.filename = filename
        self.mime_type = mime_type
        self.data = data
        self.description = description
        self.document_type = document_type
        self.encoding = "Base64"  # Standard encoding for UBL

    def load_from_file(self, file_path):
        """Load attachment data from a file.

        Parameters
        ----------
        file_path: string
            Path to the file to be attached.

        Raises
        ------
        FileNotFoundError: If the file doesn't exist.
        IOError: If the file cannot be read.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with open(file_path, 'rb') as f:
                self.data = f.read()
        except IOError as e:
            raise IOError(f"Cannot read file {file_path}: {e}")

        # Extract filename from path
        self.filename = os.path.basename(file_path)

        # Auto-detect MIME type
        self.mime_type, _ = mimetypes.guess_type(file_path)
        if self.mime_type is None:
            self.mime_type = "application/octet-stream"

    @property
    def encoded_data(self):
        """Get the base64-encoded data.

        Returns
        -------
        string
            Base64-encoded representation of the file data.
        """
        if self.data is None:
            return None
        return base64.b64encode(self.data).decode('utf-8')

    @property
    def size(self):
        """Get the size of the attachment in bytes.

        Returns
        -------
        int
            Size of the attachment in bytes, or 0 if no data.
        """
        return len(self.data) if self.data else 0

    def is_valid(self):
        """Check if the attachment is valid.

        Returns
        -------
        bool
            True if the attachment has data, filename, and MIME type.
        """
        return (self.data is not None and 
                self.filename is not None and 
                self.mime_type is not None)

    @classmethod
    def supported_mime_types(cls):
        """Get list of commonly supported MIME types for attachments.

        Returns
        -------
        list
            List of supported MIME types.
        """
        return [
            'application/pdf',
            'image/jpeg',
            'image/png',
            'image/tiff',
            'text/plain',
            'text/csv',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'application/msword',
            'application/xml',
            'text/xml',
        ]

    def __repr__(self):
        if not self.is_valid():
            return f"{self.__class__.__name__}: empty"
        return f"{self.__class__.__name__}: {self.filename} ({self.mime_type}, {self.size} bytes)"


class DocumentReference:
    """Class for representing document references in EN16931.

    Document references are used to reference external documents
    or embed attachments within the invoice/credit note.
    """

    def __init__(self, document_id=None, document_type=None, attachment=None):
        """Initialize a DocumentReference.

        Parameters
        ----------
        document_id: string (optional)
            Identifier of the referenced document.

        document_type: string (optional)
            Type/category of the document.

        attachment: Attachment (optional)
            Embedded attachment object.
        """
        self.document_id = document_id
        self.document_type = document_type
        self.attachment = attachment

    def is_valid(self):
        """Check if the document reference is valid.

        Returns
        -------
        bool
            True if has either document_id or valid attachment.
        """
        return (self.document_id is not None or 
                (self.attachment is not None and self.attachment.is_valid()))

    def __repr__(self):
        if self.attachment:
            return f"{self.__class__.__name__}: {self.document_type or 'Document'} with attachment {self.attachment.filename}"
        return f"{self.__class__.__name__}: {self.document_type or 'Document'} ID {self.document_id}"