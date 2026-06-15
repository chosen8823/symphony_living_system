from layers.base_layer import BaseLayer

# Inner layer (depth 3) -- Bose-Einstein collapse point, no sub-layers
SoundFlameLayer = BaseLayer(name="sound_flame", depth=3, oscillator_freq=1.0)

# Mid layer (depth 2)
BloodWordLayer = BaseLayer(name="blood_word", depth=2, oscillator_freq=0.5)
BloodWordLayer.sub_layers = [SoundFlameLayer]

# Outer layer (depth 1) -- 6 breaths/min
BreathLayer = BaseLayer(name="breath", depth=1, oscillator_freq=0.1)
BreathLayer.sub_layers = [BloodWordLayer]

# Canonical lookup
LAYERS = {
    "breath": BreathLayer,
    "blood_word": BloodWordLayer,
    "sound_flame": SoundFlameLayer,
}
ALL_LAYERS = [BreathLayer, BloodWordLayer, SoundFlameLayer]
