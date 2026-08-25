from omega_stress.application.pipeline.hooks.notification_hook import (
    notify_auto_stop,
    notify_local_bottleneck,
)


def test_notify_auto_stop_includes_reason():
    messages: list[str] = []

    notify_auto_stop("seuil d'erreur depasse", sink=messages.append)

    assert "seuil d'erreur depasse" in messages[0]


def test_notify_local_bottleneck_sends_a_message():
    messages: list[str] = []

    notify_local_bottleneck(sink=messages.append)

    assert len(messages) == 1
