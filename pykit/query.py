"""
Manage queries! Too much queries!
"""
import typing
from typing import Any, Literal, Self

from pykit.check import check
from pykit.err import InpErr, NotFoundErr, ValueErr
from pykit.log import log


QueryUpdOperator = Literal["set", "inc", "pull", "pop", "push", "mul"]
QueryUpdOperators = [
        "set",
        "inc",
        "pull",
        "pop",
        "push",
        "mul"]

class Query(dict[str, Any]):
    @classmethod
    def as_search_sid(cls, sid: str) -> Self:
        return typing.cast(Self, Query({"sid": sid}))

    @classmethod
    def as_upd(  # noqa: PLR0913
        cls,
        *,
        set: dict[str, Any] | None = None,
        inc: dict[str, Any] | None = None,
        push: dict[str, Any] | None = None,
        pull: dict[str, Any] | None = None,
        pop: dict[str, Any] | None = None,
    ) -> Self:
        return typing.cast(Self, Query({
            "$set": set or {},
            "$inc": inc or {},
            "$push": push or {},
            "$pull": pull or {},
            "$pop": pop or {},
        }))

    def get_upd_field(self, name: str) -> Any:
        for op_k, op_val in self.items():
            if op_k.replace("$", "") not in QueryUpdOperators:
                raise ValueErr(f"query {self} is incorrect for upd")
            for k, v in op_val.items():
                if k == name:
                    return v

        raise NotFoundErr(
                f"field with name {name} is not found in upd query {self}")

    def copy(self) -> Self:
        return typing.cast(Self, Query(super().copy()))

    def disallow(
        self,
        *disallowed_keys: str,
        raise_mod: Literal["null", "warn", "err"] = "null",
    ) -> Self:
        """
        Process this query for disallowed keys.

        Each disallowed key will be scheduled for delete, but if raise_mod
        is not "err".
        """

        keys_to_del: list[str] = []

        for k in self:
            if k in disallowed_keys:
                keys_to_del.append(k)
                self._raise_err_for_disallowed(k, raise_mod)

        for k in keys_to_del:
            del self[k]

        return self

    def _raise_err_for_disallowed(
        self,
        key: str,
        raise_mod: Literal["null", "warn", "err"],
        ):
        match raise_mod:
            case "null":
                return
            case "warn":
                log.warn(
                    f"{key} is not allowed in query => skip",
                )
            case "err":
                raise InpErr(f"{key} in query")
            case _:
                check.fail()

