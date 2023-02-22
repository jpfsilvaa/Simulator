from dataclasses import dataclass


@dataclass(frozen=True)
class VertexData:
    __slots__ = ["lat", "lon"]
    lat: float
    lon: float

    def __repr__(self) -> str:
        return f"{self.lat} {self.lon}"


@dataclass(frozen=True)
class Vertex:
    __slots__ = ["realId", "id", "data"]
    realId: int
    id: int
    data: VertexData

    @property
    def description(self) -> str:
        return f"{self.realId} {self.data}"


@dataclass(frozen=True)
class EdgeData:
    __slots__ = ["length", "highway", "max_v", "name"]
    length: float
    highway: str
    max_v: int
    name: str

    def __repr__(self) -> str:
        return f"{self.length} {self.highway} {self.max_v}"


@dataclass(frozen=True)
class Edge:
    __slots__ = ["realS", "realT", "s", "t", "forward", "backward", "data"]
    realS: int
    realT: int
    s: int
    t: int
    forward: bool
    backward: bool
    data: EdgeData

    @property
    def description(self) -> str:
        both_directions = "1" if self.forward and self.backward else "0"
        return f"{self.realS} {self.realT} {self.data} {both_directions}"
