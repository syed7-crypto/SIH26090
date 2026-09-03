# Integration

All modules should integrate around `product_id`, the common identifier for a
product across media, voice, catalogue, and pricing work.

Each module must define:

- clearly defined inputs;
- clearly defined outputs;
- predictable interfaces; and
- schema-compatible data.

Modules should be independently testable. Integration tests should verify
composition and contract compatibility rather than requiring every provider to
be available locally.

Uploaded files are represented by storage references such as `storage_path`.
The system must not assume that a stored image or audio file has a public URL;
access control and storage behavior belong to the eventual application layer.

