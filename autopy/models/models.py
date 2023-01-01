from enum import Enum


class ModelType(Enum):
    TEXT_DAVINCI_003 = "text-davinci-003"
    TEXT_DAVINCI_002 = "text-davinci-002"
    TEXT_DAVINCI_001 = "text-davinci-001"
    CODE_DAVINCI_003 = "code-davinci-002"
    CODE_DAVINCI_002 = "code-davinci-001"
    TEXT_CURIE_003 = "text-curie-003"
    TEXT_CURIE_002 = "text-curie-002"
    TEXT_CURIE_001 = "text-curie-001"



if __name__ == '__main__':
    print(ModelType.TEXT_DAVINCI_003.value)
    print(ModelType.TEXT_DAVINCI_002.value)
    print(ModelType.TEXT_DAVINCI_001.value)
    print(ModelType.CODE_DAVINCI_003.value)
    print(ModelType.CODE_DAVINCI_002.value)
    print(ModelType.TEXT_CURIE_003.value)
    print(ModelType.TEXT_CURIE_002.value)
    print(ModelType.TEXT_CURIE_001.value)
