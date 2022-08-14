from pydoc import describe
import discord
from discord.ext import commands
from utils.utils import Embed
import traceback
import akinator


class AkinatorView(discord.ui.View):
    def __init__(
        self,
        ctx: commands.Context,
        akin: akinator.Akinator,
        prev_q: str = None,
        next_q: str = None,
        q_no: int = 1,
    ) -> None:
        super().__init__()
        self.ctx = ctx
        self.akin = akin
        self.prev_question = prev_q
        self.next_question = next_q
        self.question_number = q_no

    @discord.ui.button(label="Yes", style=discord.ButtonStyle.green)
    async def yes_callback(self, button, interaction):
        # await interaction.response.defer()
        await interaction.channel.send(content="Pressed Yes")
        self.next_question = self.akinator.answer("yes")

        embed = Embed(
            title=f"Question {self.question_number}", description=self.next_question
        )

        await self.ctx.response.send_message(
            embed=embed,
            view=AkinatorView(
                self.ctx,
                self.akin,
                next_q=self.next_question,
                q_no=self.question_number + 1,
            ),
        )

    @discord.ui.button(label="Probably", style=discord.ButtonStyle.green)
    async def prob_callback(self, button, interaction):
        # await interaction.response.defer()
        self.next_question = self.akinator.answer("probably")

        embed = Embed(
            title=f"Question {self.question_number}", description=self.next_question
        )

        await self.ctx.response.send_message(
            embed=embed,
            view=AkinatorView(
                self.ctx,
                self.akin,
                next_q=self.next_question,
                q_no=self.question_number + 1,
            ),
        )

    @discord.ui.button(label="IDK", style=discord.ButtonStyle.gray)
    async def idk_callback(self, button, interaction):
        # self.next_question = self.akinator.answer("idk")

        embed = Embed(
            title=f"Question {self.question_number}", description=self.next_question
        )

        await self.ctx.response.send_message(
            embed=embed,
            view=AkinatorView(
                self.ctx,
                self.akin,
                next_q=self.next_question,
                q_no=self.question_number + 1,
            ),
        )

    @discord.ui.button(label="No", style=discord.ButtonStyle.red)
    async def no_callback(self, button, interaction):
        # self.next_question = self.akinator.answer("no")

        embed = Embed(
            title=f"Question {self.question_number}", description=self.next_question
        )

        await self.ctx.response.send_message(
            embed=embed,
            view=AkinatorView(
                self.ctx,
                self.akin,
                next_q=self.next_question,
                q_no=self.question_number + 1,
            ),
        )

    @discord.ui.button(label="Probably Not", style=discord.ButtonStyle.red)
    async def prob_not_callback(self, button, interaction):
        # self.next_question = self.akinator.answer("probably not")

        embed = Embed(
            title=f"Question {self.question_number}", description=self.next_question
        )

        await self.ctx.response.send_message(
            embed=embed,
            view=AkinatorView(
                self.ctx,
                self.akin,
                next_q=self.next_question,
                q_no=self.question_number + 1,
            ),
        )
