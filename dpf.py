import galois


SecretKey = galois.FieldArray
FieldElement = galois.FieldArray


class NaiveDPF:
    def __init__(self, GF, num_outputs: int) -> None:
        self.GF = GF
        self.num_outputs = num_outputs

    def gen_keys(self, x: int, y: FieldElement) -> tuple[SecretKey, SecretKey]:
        # Generate secret key 0 by generating a random vector
        sk_0 = self.GF.Random(self.num_outputs)

        # For all input values that are not x the two secret keys should additively cancel
        # sk_0[x'] + sk_1[x'] = 0, when x' != x
        sk_1 = -sk_0.copy()

        # Generate point y such that:
        # sk_0[x] + sk_1[x] = y
        sk_1[x] += y

        return (sk_0, sk_1)

    def eval_key(self, sk, x) -> FieldElement:
        # Evaluate the secret key at x
        return sk[x]
