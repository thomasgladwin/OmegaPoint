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
            Do not refer to anything that does not exist or that did not happen. Do not make up any false claims.
            My role is: {self.role_user}.
            My aim is: {self.aim}.
            Use the following information to help me achieve my aim: {self.information}
        """

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
                        Evaluate the following response relative to the following context.
                        The user must succeed in their role described as:{self.role_user} - consider what attributes the output should have to optimize that outcome. 
                        The response must achieve the aims described as:{self.aim}.
                        Explain everything that is wrong about the response, as critically and precisely as possible.
                        The response was: {response}.
                    """
                else:
                    critic_instructions = f"""
                        Evaluate the following response relative to the following context.
                        The user must succeed in their role described as:{self.role_user} - consider what attributes the output should have to optimize that outcome. 
                        The response must achieve the aims described as:{self.aim}.
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
                            print("\n".join(textwrap.wrap(response)))
                        pass
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

            adjusterinstructions = f"""
                Create a new LLM prompt as specified below. Ensure the prompt remains suitable for:
                the role of {self.role_user} and the aim of {self.aim}.
                The prompt must ensure outputs do not refer to anything that does not exist or that did not happen, or make up any false claims.
                The criticism of the output generated by the prompt was as follows, between the symbols [[[ and ]]]: [[[{criticism}]]]
                The original prompt was as follows:
                {prompt}
            """
            adjuster = ChatBot.ChatBot()
            response = adjuster.send_query(adjusterinstructions)
            parts = str.split(response, "</think>")
            prompt = str.strip(parts[-1])
            if self.verbose:
                print("\n###\n### Adjuster\n###\n")
                print("\n".join(textwrap.wrap(response)))

        # Get best output
        best_score = self.scores[0]
        for iScore in range(1, len(self.scores)):
            score = self.scores[iScore]
            if score > best_score:
                best_score = score
                output = self.output_history[iScore]

        print("\n".join(textwrap.wrap(output)))
        History = {}
        History['Prompt'] = self.prompt_history
        History["Output"] = self.output_history
        History["Criticism"] = self.criticism_history
        History["Score"] = self.scores
        History["Score_NegPos"] = self.scores_neg_pos
        return output, History
