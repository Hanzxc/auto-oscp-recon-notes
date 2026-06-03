"""Data models for parsed reconnaissance results.

The model is intentionally tiny. The MVP only needs a clean, normalized
representation of a single service so the rest of the tool (templates, report,
JSON export) can stay simple and well tested.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Service:
    """A single network service discovered on a host.

    ``scripts`` maps an Nmap NSE script id to its raw output. It uses
    ``compare=False`` so the frozen dataclass stays hashable: a plain ``dict``
    field is unhashable, and ``frozen=True`` otherwise folds every field into
    the generated ``__hash__``.
    """

    host: str
    port: int
    protocol: str
    name: str
    state: str
    product: str = ""
    version: str = ""
    extra_info: str = ""
    scripts: dict[str, str] = field(default_factory=dict, compare=False)

    @property
    def endpoint(self) -> str:
        """Human-readable ``port/proto`` label, e.g. ``80/tcp``."""
        return f"{self.port}/{self.protocol}"

    @property
    def product_version(self) -> str:
        """Combined ``product version`` string, blank if neither is known."""
        return " ".join(part for part in (self.product, self.version) if part).strip()

    def to_dict(self) -> dict:
        """Serialize to a plain JSON-friendly dictionary."""
        return {
            "host": self.host,
            "port": self.port,
            "protocol": self.protocol,
            "name": self.name,
            "state": self.state,
            "product": self.product,
            "version": self.version,
            "extra_info": self.extra_info,
            "scripts": dict(self.scripts),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Service":
        """Rebuild a :class:`Service` from :meth:`to_dict` output."""
        return cls(
            host=data.get("host", ""),
            port=int(data.get("port", 0)),
            protocol=data.get("protocol", ""),
            name=data.get("name", ""),
            state=data.get("state", ""),
            product=data.get("product", ""),
            version=data.get("version", ""),
            extra_info=data.get("extra_info", ""),
            scripts=dict(data.get("scripts", {})),
        )
