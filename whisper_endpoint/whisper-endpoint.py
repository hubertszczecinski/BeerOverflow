import numpy as np
import stable_whisper
import ray
from starlette.requests import Request
from ray import serve
import torch

from whisper_endpoint.id_matching import Matcher


#serve run whisper-endpoint:depl


@serve.deployment(ray_actor_options={"num_cpus": 1})
class ModelDeployment:
    def __init__(self):
        self.model = stable_whisper.load_model("base")
        self.matcher = Matcher("../id.csv")


    async def __call__(self, request: Request):
        request = await request.body()
        data = np.frombuffer(request, np.float32)
        #separated = self.separator.separate_batch(torch.from_numpy(data).unsqueeze(0)) separated[0, :, 0]
        out = self.model.transcribe(audio=data, language="en", verbose=True, vad=True, only_voice_freq=True)
        segments = out.to_dict()["segments"]
        print(len(segments))
        if len(segments) == 0:
            return ""
        return self.matcher.match(out.text)


ray.init()
depl = ModelDeployment.bind()

#serve.run(depl, route_prefix="/")


"""data = librosa.load("audio.m4a")
resampled = librosa.resample(data[0], orig_sr=data[1], target_sr=16000)

result = model.transcribe(audio=resampled, verbose=True, language="pl", vad=True, only_voice_freq=True)
result.remove_repetition(5)
# if len(result.to_dict()["segments"]) == 0 or len(result.to_dict()["segments"][-1]["words"]) == 0:
# return " "


print(result.to_dict()["segments"][0]["text"])"""
