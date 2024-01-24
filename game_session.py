class GameSession:
    def __init__(self):
        self.bot_wins_count = 0
        self.user_wins_count = 0
        self.rounds_played_count = 0
        self.game_moves = ('Камінь', 'Бумага', 'Ножиці')
        self.chat_id = None
        self.win_combinations = {'Камінь': 'Ножиці',
                                 'Бумага': 'Камінь',
                                 'Ножиці': 'Бумага', }

    async def play_round(self, bot_choice: str, user_choice: str) -> str:
        if self.win_combinations[bot_choice] == user_choice:
            self.bot_wins_count += 1
            decision = 'Бот вас переграв :('
        elif bot_choice == user_choice:
            decision = 'Нічия, вгадуй краще!'
        else:
            self.user_wins_count += 1
            decision = 'Ви перемогли в бота!'
        self.rounds_played_count += 1
        return decision

    async def show_results(self) -> str:
        user_wining_frequency = (self.user_wins_count / self.rounds_played_count) * 100
        bot_wining_frequency = (self.bot_wins_count / self.rounds_played_count) * 100
        game_results = (f"Результати нашої гри наступні:\n"
                        f" - зіграно раундів: {self.rounds_played_count};\n"
                        f" - переможено/програно: {self.user_wins_count}/{self.bot_wins_count};\n"
                        f" - частота ваших перемог: {user_wining_frequency:.3}%;\n"
                        f" - частота перемог бота: {bot_wining_frequency:.3}%.\n\n") + await self._make_final_decision()
        return game_results

    async def _make_final_decision(self):
        if self.user_wins_count > self.bot_wins_count:
            return 'Ви перемогли силу рандому...\nВам є чим пишатися!'
        elif self.user_wins_count < self.bot_wins_count:
            return 'Ви програли...\nМожливо, коли-небудь ChatGPT відбере у Вас роботу.'
        else:
            return 'Нічия! Не розстраюйся :D'
