from enum import Enum


class ScopeEnum(str, Enum):
    didr_write = "openid didr_write"
    didr_invite = "openid didr_invite"
    tir_write = "openid tir_write"
    tir_invite = "openid tir_invite"
    timestamp_write = "openid timestamp_write"
    tnt_authorise = "openid tnt_authorise"
    tnt_create = "openid tnt_create"
    tnt_write = "openid tnt_write"
    tpr_write = "openid tpr_write"
    tsr_write = "openid tsr_write"
