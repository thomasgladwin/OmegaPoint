import textwrap
import ChatBot
from importlib import reload
reload(ChatBot)

class OmegaPoint():
    def __init__(self, role_user, aim, information, min_iterations=5, max_iterations=10, verbose=False, neg_pos_balance = 0.5):
        self.role_user = role_user
        self.aim = aim
        self.information = information
        self.min_iterations = min_iterations
        self.max_iterations = max_iterations
        self.verbose = verbose
        self.neg_pos_balance = neg_pos_balance

        self.prompt_history = []
        self.output_history = []
        self.criticism_history = []
        self.scores = []
        self.scores_neg_pos = []

    def run(self):
        output = ""
        prompt = f"""
            Your role is between ###ROLE### and ###ROLEEND###: ###ROLE### {self.role_user} ###ROLEEND###.
            Your aim ism between ###AIM### and ###AIMEND###: ###AIM###: {self.aim} ###AIMEND###.
            Use the following information to help you achieve your aim: {self.information}
        """

        prev_score = -1
        for n in range(self.max_iterations):
            print(f"Iteration {n} of {self.max_iterations}")
            actor = ChatBot.ChatBot()
            self.prompt_history.append(prompt)
            response = actor.send_query(prompt)
            parts = str.split(response, "</think>")
            output = str.strip(parts[-1])
            self.output_history.append(output)

            if self.verbose:
                print("\n###\n### Actor\n###\n")
                print("\n".join(textwrap.wrap(output)))

            scores_neg_pos = []
            for neg_pos in range(2):
                if neg_pos == 0:
                    critic_instructions = f"""
                        Evaluate the following response specifically nad exclusive  relative to the following context; do not apply any other considerations. 
                        Focus on what was misaligned about the response, on any information it failed to use, or where it did not fit the role or aims.
                        The user must succeed in their role described between ###ROLE### and ###ENDROLE### as ###ROLE###:{self.role_user} ###ENDROLE### - consider what attributes the output should have to optimize that outcome. 
                        The response must achieve the aims described between ###AIM### and ###ENDAIM### as ###AIM###: {self.aim} ###ENDAIM###.
                        The response must follow the information between ###INFO### and ###ENDINFO### as ###INFO###: {self.information} ###ENDINFO###.
                        The response was: {response}.
                    """
                else:
                    critic_instructions = f"""
                        Evaluate the following response specifically nad exclusive relative to the following context; do not apply any other considerations. 
                        Focus on what was aligned about the response, on any information it creatively used and elaborated on, or where it clearly reflected the role or aims.
                        The user must succeed in their role described between ###ROLE### and ###ENDROLE### as ###ROLE###:{self.role_user} ###ENDROLE### - consider what attributes the output should have to optimize that outcome. 
                        The response must achieve the aims described between ###AIM### and ###ENDAIM### as ###AIM###: {self.aim} ###ENDAIM###.
                        The response must follow the information between ###INFO### and ###ENDINFO### as ###INFO###: {self.information} ###ENDINFO###.
                        Explain everything that is good about the response, as enthusiastically and clearly as possible.
                        The response was: {response}.
                    """
                critic = ChatBot.ChatBot()
                response = critic.send_query(critic_instructions)
                parts = str.split(response, "</think>")
                criticism = str.strip(parts[-1])
                self.criticism_history.append(criticism)
                if self.verbose:
                    print("\n###\n### Critic\n###\n")
                    print("\n".join(textwrap.wrap(criticism)))

                score = -1
                while score < 0:
                    scorer_instructions = f"""
                        Provide a score, as a whole number from 0 (extremely bad) to 100 (extremely good), based on the criticism below.
                        The harsher and more justified the criticism, the lower the score.
                        The more positive the criticism, the higher the score.
                        Only print out the score as the output, with no other text around it.
                        The criticism was: {criticism}.
                    """
                    scorer = ChatBot.ChatBot()
                    response = scorer.send_query(scorer_instructions)
                    parts = str.split(response, "</think>")
                    score_text = str.strip(parts[-1])
                    try:
                        score = int(score_text)
                    except:
                        print("\n!!!! Error in scoring output. Response was:")
                        if self.verbose:
                            print("\nResponse: ".join(textwrap.wrap(response)))
                            print("\nTo criticism: ".join(textwrap.wrap(criticism)))
                        score = -11
                        break
                scores_neg_pos.append(score)

            self.scores_neg_pos.append(scores_neg_pos)
            score = self.neg_pos_balance * scores_neg_pos[1] + (1 - self.neg_pos_balance) * scores_neg_pos[0]
            self.scores.append(score)
            if self.verbose:
                print(f"\n###\n### Score\n###\n{score}")

            # Check for convergence
            for old_score in self.scores:
                if score < old_score:
                    if n >= self.min_iterations:
                        break

            if score > 0 and score > prev_score:
                adjusterinstructions = f"""
                    Create a new LLM prompt as specified below. Ensure the prompt remains suitable for:
                    the role (specified between ###ROLE### and ###ROLEEND###) of ###ROLE### {self.role_user} ###ROLEEND### and the aim (specified between ###AIM### and ###AIMEND###) of ###AIM### {self.aim} ###AIMEND###.
                    The criticism of the output generated by the prompt was as follows, between the symbols [[[ and ]]]: [[[{criticism}]]]
                    The original prompt was as follows, given between ###PROMPT### and ###ENDPROMPT###.\n###PROMPT### \n
                    {prompt}
                    \n ###ENDPROMPT### . Use the following information to inform the new prompt: {self.information}
                """
                adjuster = ChatBot.ChatBot()
                response = adjuster.send_query(adjusterinstructions)
                parts = str.split(response, "</think>")
                prompt = str.strip(parts[-1])
                if self.verbose:
                    print("\n###\n### Adjuster\n###\n")
                    print("\n".join(textwrap.wrap(response)))

            prev_score = score

        # Get best output
        best_score = self.scores[0]
        for iScore in range(1, len(self.scores)):
            score = self.scores[iScore]
            if score > best_score:
                best_score = score
                output = self.output_history[iScore]

        #print("\n".join(textwrap.wrap(output)))
        print("print(\"\\n\".join(textwrap.wrap(output))")
        History = {}
        History['Prompt'] = self.prompt_history
        History["Output"] = self.output_history
        History["Criticism"] = self.criticism_history
        History["Score"] = self.scores
        History["Score_NegPos"] = self.scores_neg_pos
        return output, History
