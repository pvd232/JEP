"""CPU-only tokenizer replay compatibility, never a model/generation modification.

Tokenizers0.23 normalizes Go's serialized normalized=True special-token metadata
through the metaspace normalizer when loading. Actual TF4.34/Tokenizers0.14
CodeLlamaTokenizerFast decodes declared EOS2 as </s>, and skips it. A separate
in-memory decode tokenizer registers the same declared special IDs/content
without normalizing those metadata strings. Encoding uses the original pinned
JSON unchanged. Token IDs, vocab/merges, decoder and generated text are not edited.
"""
from pathlib import Path
import hashlib
import json

GO_TOKENIZER_SHA256='3133bbcd5bf9bae98264c4c081882eef2ceccf9ab6fc9a8dfbcf1f72dbd7a21c'


def codec(model,tokenizer_path):
    from tokenizers import Tokenizer
    if model not in {'knowcoder','gollie'}:raise ValueError('Unknown pinned native tokenizer')
    path=Path(tokenizer_path);raw=path.read_bytes()
    encoder=Tokenizer.from_file(str(path));decoder=encoder
    if model=='gollie':
        if hashlib.sha256(raw).hexdigest()!=GO_TOKENIZER_SHA256:
            raise ValueError('CPU Go decoder compatibility requires exact pinned tokenizer bytes')
        document=json.loads(raw)
        declared={t['id']:t['content'] for t in document['added_tokens'] if t.get('special')}
        if any(declared.get(i)!=s for i,s in {0:'<unk>',1:'<s>',2:'</s>'}.items()):
            raise ValueError('Pinned Go special-token identity changed')
        for token in document['added_tokens']:
            if token.get('special'):token['normalized']=False
        decoder=Tokenizer.from_str(json.dumps(document,ensure_ascii=False))
        if any(decoder.id_to_token(i)!=s for i,s in declared.items()):
            raise ValueError('CPU decoder did not preserve declared special-token IDs/content')
        if decoder.decode([2],skip_special_tokens=True)!='' or decoder.decode([2],skip_special_tokens=False)!='</s>':
            raise ValueError('CPU decoder EOS compatibility check failed')
    class Codec:
        def encode(self,text):
            ids=encoder.encode(text,add_special_tokens=True).ids
            if model=='gollie' and ids and ids[-1]==2:ids=ids[:-1]
            return ids
        def count_tokens(self,text):return len(self.encode(text))
        def decode(self,ids,skip_special_tokens=False):return decoder.decode(ids,skip_special_tokens=skip_special_tokens)
    return Codec()


def implementation_identity():
    return {'module_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'generation_changed':False,'encoder_json_unchanged':True,
        'compatibility_scope':'CPU replay decode only; Go declared special metadata normalization',
        'go_tokenizer_sha256':GO_TOKENIZER_SHA256}
