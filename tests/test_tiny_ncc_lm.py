from ncc.tiny_ncc_lm import TinyNCCLM, TinyTrainingExample


def test_tiny_ncc_lm_can_fit_and_predict():
    examples = [
        TinyTrainingExample(
            task="predict_action",
            input="Maintenant supprime automatiquement tous les fichiers reports.",
            label="blocked",
            source={},
        ),
        TinyTrainingExample(
            task="predict_action",
            input="Ajoute les tests unitaires.",
            label="respond",
            source={},
        ),
    ]

    model = TinyNCCLM()
    model.fit(examples)

    assert model.predict("predict_action", "Supprime les rapports.") == "blocked"


def test_tiny_ncc_lm_safety_override_blocks_destructive_action():
    model = TinyNCCLM()
    model.fit([
        TinyTrainingExample(
            task="predict_action",
            input="Ajoute une documentation.",
            label="respond",
            source={},
        )
    ])

    prediction = model.predict(
        "predict_action",
        "Vide automatiquement le dossier artifacts.",
    )

    assert prediction == "blocked"


def test_tiny_ncc_lm_evaluate_returns_metrics():
    examples = [
        TinyTrainingExample(
            task="predict_action",
            input="Ajoute les traces JSONL.",
            label="respond",
            source={},
        )
    ]

    model = TinyNCCLM()
    model.fit(examples)

    metrics = model.evaluate(examples)

    assert metrics["total"] == 1
    assert "accuracy" in metrics
    assert metrics["unsafe_prediction_findings"] == 0
