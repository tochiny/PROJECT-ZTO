import discord
import asyncio
import json
import random
import traceback
from bs4 import BeautifulSoup
import requests
from discord import Interaction, app_commands
from discord.ext import commands, tasks

colors = [
    0xFFE4E1, 0x00FF7F, 0xD8BFD8, 0xDC143C, 0xFF4500, 0xDEB887, 0xADFF2F,
    0x800000, 0x4682B4, 0x006400, 0x808080, 0xA0522D, 0xF08080, 0xC71585,
    0xFFB6C1, 0x00CED1
]


class ToolsManhwa:

    def __init__(self, client):
        self.client = client
        self.database = client.database
        self.organize = client.organize
        self.data = client.data
        self.colors = colors

    def showTitleFromNumber(self, idserver: str, number: int):
        return list(self.database[idserver]["manhwa"]["title"])[number - 1]

    def checkNumber(self, idserver: str, number: int):
        if not number.isdigit():
            return None
        if int(number) > len(list(self.database[idserver]["manhwa"]["title"])):
            return False
        else:
            if int(number) <= 0:
                return False
        return True

    def checkTitle(self, idserver: str, title: str):
        for title_args in self.database[idserver]["manhwa"]["title"]:
            if title.lower() == title_args.lower():
                return True, title_args
        return False, None

    def getInfo(self, title: str, idserver: str):
        if idserver not in self.database:
            return False, []
        else:
            if title not in self.database[idserver]["manhwa"]["title"]:
                return False, []
            else:
                n = 1
                for titleN in self.database[idserver]["manhwa"]["title"]:
                    if titleN == title:
                        break
                    n += 1
                number = str(n)
                titleName = str(title)
                chapter = str(self.database[idserver]["manhwa"]["title"][title]
                              ["chapter"])
                return True, [number, titleName, chapter]

    def getInfoSerVer(self, idserver: str):
        if self.database[str(idserver)]["manhwa"]["title"] == {}:
            return False
        else:
            return True

    def menuEmbed(self, idserver):
        dictData, pageAll, chapterAll = self.organize.abbreviationLetter(
            list(self.database[str(idserver)]["manhwa"]["title"]),
            int(self.database[str(idserver)]["manhwa"]["settings"]["limit"]))
        self.database[str(idserver)]["manhwa"]["control"]["pageall"] = str(
            pageAll)
        self.database[str(idserver)]["manhwa"]["control"]["chapterall"] = str(
            chapterAll)
        page = self.database[str(idserver)]["manhwa"]["control"]["page"]
        sortDict = dictData[self.database[str(idserver)]["manhwa"]["control"]
                            ["page"]]
        numberNow = self.database[str(
            idserver)]["manhwa"]["control"]["chapter"]
        if not self.getInfoSerVer(str(idserver)):
            embed = discord.Embed(title="ไม่พบข้อมูลในเซิฟเวอร์นี้",
                                  color=random.choice(self.colors))
            return embed, False
        else:
            titleName = list(
                self.database[str(idserver)]["manhwa"]["title"])[int(numberNow)
                                                                 - 1]
            chapterNow = self.database[str(
                idserver)]["manhwa"]["title"][titleName]["chapter"]
            embed = discord.Embed(
                title=f"ลำดับที่ {numberNow} ตอนที่ {chapterNow}",
                description=f"หน้า {page}/{pageAll}",
                color=random.choice(self.colors))
            embed.set_author(name=titleName,
                             url=self.database[str(idserver)]["manhwa"]
                             ["title"][titleName]["link"],
                             icon_url=self.database[str(idserver)]["manhwa"]
                             ["title"][titleName]["image"])
            for title in sortDict:
                chapter = self.database[str(
                    idserver)]["manhwa"]["title"][title]["chapter"]
                embed.add_field(name=f"   {sortDict[title]}. {title}",
                                value=f"ตอนที่ {chapter}",
                                inline=False)
                embed.set_thumbnail(url=self.database[str(idserver)]["manhwa"]
                                    ["title"][titleName]["image"])
            embed.set_footer(
                text=
                f" มีจำนวนเรื่องทั้งหมด {len(self.database[str(idserver)]['manhwa']['title'])}"
            )
            return embed, True

    def infoEmbed(self, idserver, title):
        value, agrs = self.getInfo(str(title), str(idserver))
        if value:
            number = agrs[0]
            title = agrs[1]
            chapter = agrs[2]
        embed = discord.Embed(title=f"ลำดับที่ {number}",
                              description=f"ตอนที่ {chapter}",
                              color=random.choice(self.colors))
        embed.set_author(
            name=title,
            url=self.database[str(idserver)]["manhwa"]["title"][title]["link"],
            icon_url=self.database[str(
                idserver)]["manhwa"]["title"][title]["image"])
        embed.set_thumbnail(url=self.database[str(idserver)]["manhwa"]["title"]
                            [title]["image"])
        embed.set_footer(
            text=
            f" มีจำนวนเรื่องทั้งหมด {len(self.database[str(idserver)]['manhwa']['title'])}"
        )
        return embed

    def saveBackup(self, idserver):
        back_up = "รายชื่อมังฮวามั้งหมด:"
        n = 1
        for title in list(self.database[str(idserver)]["manhwa"]["title"]):
            chapter = self.database[str(
                idserver)]["manhwa"]["title"][title]["chapter"]
            back_up += f"\n{n}. {title} ตอนที่ {chapter}"
            n += 1
        self.data.saveText(back_up)

    def checkNumberOnPage(self, idserver, number):
        limit = int(
            self.database[str(idserver)]["manhwa"]["settings"]["limit"])
        chapterall = int(
            self.database[str(idserver)]["manhwa"]["control"]["chapterall"])
        dict_ = {}
        set = 1
        dict_[set] = {}
        for n in range(chapterall):
            n += 1
            dict_[set][n] = set
            if len(dict_[set]) == limit:
                set += 1
                dict_[set] = {}
        for page in dict_:
            for num in dict_[page]:
                if num == number:
                    return dict_[page][num]


class ButtonMenuManhwa(discord.ui.View):

    def __init__(self, client):
        super().__init__(timeout=None)
        self.client = client
        self.database = client.database
        self.organize = client.organize
        self.data = client.data
        self.toolsmanhwa = ToolsManhwa(client)

    @discord.ui.button(label="<<", style=discord.ButtonStyle.green)
    async def button_back_page(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        try:
            self.database[str(
                interaction.guild.id)]["manhwa"]["control"]["page"] = str(
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["page"]) - 1)
            if int(self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["page"]) <= 0:
                self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["page"] = "1"
                button.disabled = True
                await interaction.response.defer()
                await interaction.followup.edit_message(interaction.message.id,
                                                        view=self)
            else:
                self.database[str(
                    interaction.guild.id
                )]["manhwa"]["control"]["chapter"] = str(
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["chapter"]) -
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["settings"]["limit"]))
                if int(self.database[str(interaction.guild.id)]["manhwa"]
                       ["control"]["chapter"]) <= 0:
                    self.database[str(interaction.guild.id
                                      )]["manhwa"]["control"]["chapter"] = "1"
                page = self.toolsmanhwa.checkNumberOnPage(
                    interaction.guild.id,
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["chapter"]))
                self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["page"] = str(
                        page)
                bott = self.children[3]
                if bott.disabled:
                    bott.disabled = False
                embed, check = self.toolsmanhwa.menuEmbed(interaction.guild.id)
                await interaction.response.defer()
                await interaction.followup.edit_message(interaction.message.id,
                                                        embed=embed,
                                                        view=self)
        except:
            traceback.print_exc()

    @discord.ui.button(label="<", style=discord.ButtonStyle.secondary)
    async def button_back(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        try:
            self.database[str(
                interaction.guild.id)]["manhwa"]["control"]["chapter"] = str(
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["chapter"]) - 1)
            if int(self.database[str(interaction.guild.id)]["manhwa"]
                   ["control"]["chapter"]) <= 0:
                self.database[str(interaction.guild.id
                                  )]["manhwa"]["control"]["chapter"] = "1"
                button.disabled = True
                await interaction.response.defer()
                await interaction.followup.edit_message(interaction.message.id,
                                                        view=self)
            else:
                page = self.toolsmanhwa.checkNumberOnPage(
                    interaction.guild.id,
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["chapter"]))
                self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["page"] = str(
                        page)
                bott = self.children[1]
                if bott.disabled:
                    bott.disabled = False
                embed, check = self.toolsmanhwa.menuEmbed(interaction.guild.id)
                await interaction.response.defer()
                await interaction.followup.edit_message(interaction.message.id,
                                                        embed=embed,
                                                        view=self)
        except:
            traceback.print_exc()

    @discord.ui.button(label=">", style=discord.ButtonStyle.secondary)
    async def button_next(self, interaction: discord.Interaction,
                          button: discord.ui.Button):
        try:
            self.database[str(
                interaction.guild.id)]["manhwa"]["control"]["chapter"] = str(
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["chapter"]) + 1)
            if int(
                    self.database[str(interaction.guild.id)]["manhwa"]
                ["control"]["chapter"]) >= int(self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["chapterall"]):
                self.database[str(
                    interaction.guild.id
                )]["manhwa"]["control"]["chapter"] = self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["chapterall"]
                button.disabled = True
                await interaction.response.defer()
                await interaction.followup.edit_message(interaction.message.id,
                                                        view=self)
            else:
                page = self.toolsmanhwa.checkNumberOnPage(
                    interaction.guild.id,
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["chapter"]))
                self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["page"] = str(
                        page)
                bott = self.children[1]
                if bott.disabled:
                    bott.disabled = False
                embed, check = self.toolsmanhwa.menuEmbed(interaction.guild.id)
                await interaction.response.defer()
                await interaction.followup.edit_message(interaction.message.id,
                                                        embed=embed,
                                                        view=self)
        except:
            traceback.print_exc()

    @discord.ui.button(label=">>", style=discord.ButtonStyle.green)
    async def button_next_page(self, interaction: discord.Interaction,
                               button: discord.ui.Button):
        try:
            self.database[str(
                interaction.guild.id)]["manhwa"]["control"]["page"] = str(
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["page"]) + 1)
            if int(self.database[str(interaction.guild.id)]["manhwa"]
                   ["control"]["page"]) >= int(self.database[str(
                       interaction.guild.id)]["manhwa"]["control"]["pageall"]):
                self.database[str(
                    interaction.guild.id
                )]["manhwa"]["control"]["page"] = self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["pageall"]
                button.disabled = True
                await interaction.response.defer()
                await interaction.followup.edit_message(interaction.message.id,
                                                        view=self)
            else:
                self.database[str(
                    interaction.guild.id
                )]["manhwa"]["control"]["chapter"] = str(
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["chapter"]) +
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["settings"]["limit"]))
                if int(self.database[str(interaction.guild.id)]["manhwa"]
                       ["control"]["chapter"]) >= int(self.database[str(
                           interaction.guild.id)]["manhwa"]["control"]
                                                      ["chapterall"]):
                    self.database[str(
                        interaction.guild.id
                    )]["manhwa"]["control"]["chapter"] = str(self.database[str(
                        interaction.guild.id)]["manhwa"]["control"]
                                                             ["chapterall"])
                page = self.toolsmanhwa.checkNumberOnPage(
                    interaction.guild.id,
                    int(self.database[str(interaction.guild.id)]["manhwa"]
                        ["control"]["chapter"]))
                self.database[str(
                    interaction.guild.id)]["manhwa"]["control"]["page"] = str(
                        page)
                bott = self.children[0]
                if bott.disabled:
                    bott.disabled = False
                embed, check = self.toolsmanhwa.menuEmbed(interaction.guild.id)
                await interaction.response.defer()
                await interaction.followup.edit_message(interaction.message.id,
                                                        embed=embed,
                                                        view=self)
        except:
            traceback.print_exc()


class Manhwa(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.database = client.database
        self.organize = client.organize
        self.data = client.data
        self.toolsmanhwa = ToolsManhwa(client)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        try:
            if message.author.bot:
                return
            guild = message.guild
            if str(guild.id) in self.database:
                if "manhwa" in self.database[str(guild.id)]:
                    check, args = self.toolsmanhwa.checkTitle(
                        str(guild.id), str(message.content))
                    if check:
                        title = args
                        embed = self.toolsmanhwa.infoEmbed(guild.id, title)
                        await message.channel.send(embed=embed)
                    if " ตอนที่ " in message.content:
                        title = message.content.split(" ตอนที่ ")[0]
                        chapter = message.content.split(" ตอนที่ ")[1]
                        if title not in self.database[str(
                                guild.id)]["manhwa"]["title"]:
                            await message.channel.send(
                                f"ไม่พบ ชื่อเรื่อง '{title}' อยู่ในระบบ")
                        else:
                            self.database[str(guild.id)]["manhwa"]["title"][
                                title]["chapter"] = str(chapter)
                            self.database[str(
                                guild.id
                            )]["manhwa"]["title"][title]["link"] = ""
                            self.database[str(
                                guild.id
                            )]["manhwa"]["title"][title]["image"] = ""
                            await message.channel.send(
                                f"set manhwa ชื่อเรื่อง '{title}' ตอนที่ '{chapter}' เสร็จสิ้น"
                            )
        except:
            traceback.print_exc()

    @app_commands.command(name="manhwa_setup", description="setup ระบบมังฮวา")
    async def manhwa_setup(self, interaction: Interaction):
        ctx = await self.client.get_context(interaction)
        guild = ctx.message.guild
        if str(guild.id) not in self.database:
            self.database[str(guild.id)] = {}
        if "manhwa" in self.database[str(guild.id)]:
            await interaction.response.send_message(
                "เคย setup manhwa ในเซิร์ฟเวอร์นี้แล้ว")
        else:
            self.database[str(guild.id)]["manhwa"] = {}
            channel = await guild.create_text_channel("manhwa-chapter")
            self.database[str(guild.id)]["manhwa"]["id"] = str(channel.id)
            self.database[str(guild.id)]["manhwa"]["title"] = {}
            self.database[str(guild.id)]["manhwa"]["control"] = {}
            self.database[str(guild.id)]["manhwa"]["control"]["page"] = "1"
            self.database[str(guild.id)]["manhwa"]["control"]["pageall"] = "0"
            self.database[str(guild.id)]["manhwa"]["control"]["chapter"] = "1"
            self.database[str(
                guild.id)]["manhwa"]["control"]["chapterall"] = "0"
            self.database[str(guild.id)]["manhwa"]["settings"] = {}
            self.database[str(guild.id)]["manhwa"]["settings"]["limit"] = "10"
            await interaction.response.send_message(
                "setup ในเซิร์ฟเวอร์นี้เสร็จสิ้น")

    @app_commands.command(name="manhwa_list",
                          description="เช็ครายการ manhwa list ในระบบ")
    async def manhwa_list(self, interaction: Interaction):
        ctx = await self.client.get_context(interaction)
        guild = ctx.message.guild
        if str(guild.id) not in self.database:
            await interaction.response.send_message(
                "กรุณา setup ระบบในเซิร์ฟเวอร์นี้ก่อน")
        else:
            if "manhwa" not in self.database[str(guild.id)]:
                await interaction.response.send_message(
                    "กรุณาใช้คำสั่ง manhwa_setup เพื่อ setup ระบบ manhwa ก่อนใช้งาน"
                )
            else:
                await interaction.response.defer(ephemeral=True)
                view = ButtonMenuManhwa(self.client)
                embed, check = self.toolsmanhwa.menuEmbed(guild.id)
                self.toolsmanhwa.saveBackup(guild.id)
                if check:
                    await interaction.followup.send(embed=embed,
                                                    view=view,
                                                    ephemeral=True,
                                                    wait=True)
                    with open(self.data.text_path, "rb") as file:
                        await interaction.followup.send(
                            file=discord.File(file, self.data.text_path))
                else:
                    await interaction.followup.send(embed=embed,
                                                    ephemeral=True,
                                                    wait=True)

    @app_commands.command(name="manhwa_info",
                          description="เช็คข้อมูล manhwa ในระบบ")
    @app_commands.describe(title='ใส่ชื่อเรื่อง')
    async def manhwa_info(self, interaction: Interaction, title: str):
        ctx = await self.client.get_context(interaction)
        guild = ctx.message.guild
        if str(guild.id) not in self.database:
            await interaction.response.send_message(
                "กรุณา setup ระบบในเซิร์ฟเวอร์นี้ก่อน")
        else:
            if "manhwa" not in self.database[str(guild.id)]:
                await interaction.response.send_message(
                    "กรุณาใช้คำสั่ง 'manhwa_setup' เพื่อ setup ระบบ manhwa ก่อนใช้งาน"
                )
            else:
                check, args = self.toolsmanhwa.checkTitle(
                    str(guild.id), str(title))
                if not check:
                    await interaction.response.send_message(
                        f"ไม่พบ manhwa ชื่อเรื่อง '{title}' ในระบบ")
                else:
                    title = args
                    await interaction.response.defer(ephemeral=True)
                    embed = self.toolsmanhwa.infoEmbed(guild.id, title)
                    await interaction.followup.send(embed=embed,
                                                    ephemeral=True)

    @app_commands.command(name="manhwa_set",
                          description="ตั้งชื่อเรื่อง manhwa และตอนที่อ่าน")
    @app_commands.choices(type=[
        app_commands.Choice(name="ใส่ชื่อเรื่อง", value="1"),
        app_commands.Choice(name="ใส่ลำดับเรื่อง", value="2")
    ])
    @app_commands.describe(type='ใส่ประเภทของข้อมูล')
    @app_commands.describe(title='ใส่ชื่อเรื่อง หรือ ลำดับเรื่อง')
    @app_commands.describe(chapter='ใส่ตอนที่อ่าน')
    async def manhwa_set(self, interaction: Interaction,
                         type: app_commands.Choice[str], title: str or int,
                         chapter: int):
        ctx = await self.client.get_context(interaction)
        guild = ctx.message.guild
        if str(guild.id) not in self.database:
            await interaction.response.send_message(
                "กรุณา setup ระบบในเซิร์ฟเวอร์นี้ก่อน")
        else:
            if "manhwa" not in self.database[str(guild.id)]:
                await interaction.response.send_message(
                    "กรุณาใช้คำสั่ง 'manhwa_setup' เพื่อ setup ระบบ manhwa ก่อนใช้งาน"
                )
            else:

                class ButtonConfirmMannhwaSet(discord.ui.View):

                    def __init__(self, client, ctx: commands.Context,
                                 title: str, chapter: int):
                        super().__init__()
                        self.client = client
                        self.database = client.database
                        self.organize = client.organize
                        self.getMangawa = client.getMangawa
                        self.data = client.data

                    @discord.ui.button(label="ตกลง",
                                       style=discord.ButtonStyle.green)
                    async def button_confirm(self,
                                             interaction: discord.Interaction,
                                             button: discord.ui.Button):
                        for button in self.children:
                            button.disabled = True
                        await interaction.response.edit_message(view=self)
                        if title not in self.database[str(
                                interaction.guild.id)]["manhwa"]["title"]:
                            self.database[str(
                                interaction.guild.id
                            )]["manhwa"]["title"][title] = {}
                        self.database[str(
                            interaction.guild.id
                        )]["manhwa"]["title"][title]["chapter"] = str(chapter)
                        self.database[str(
                            interaction.guild.id
                        )]["manhwa"]["title"][title]["link"] = ""
                        self.database[str(
                            interaction.guild.id
                        )]["manhwa"]["title"][title]["image"] = ""
                        await ctx.send(
                            f"set manhwa ชื่อเรื่อง '{title}' ตอนที่ '{chapter}' เสร็จสิ้น"
                        )
                        url, link = self.getMangawa.getInfoManhwa(title)
                        self.database[str(
                            guild.id
                        )]["manhwa"]["title"][title]["image"] = link
                        self.database[str(
                            guild.id)]["manhwa"]["title"][title]["link"] = url

                    @discord.ui.button(label="ยกเลิก",
                                       style=discord.ButtonStyle.red)
                    async def button_cancel(self,
                                            interaction: discord.Interaction,
                                            button: discord.ui.Button):
                        for button in self.children:
                            button.disabled = True
                        await interaction.response.edit_message(view=self)
                        await ctx.send("ยกเลิกรายการ")

                passForSend = False
                if type.value == '1':
                    passForSend = True
                elif type.value == '2':
                    check = self.toolsmanhwa.checkNumber(str(guild.id), title)
                    if check == None:
                        await interaction.response.send_message(
                            f"คุณเลือกชนิดเป็นการใส่ลำดับเรื่อง โปรดระบุเป็นลำดับเลือกใหม่อีกครั้ง"
                        )
                    elif check == False:
                        await interaction.response.send_message(
                            f"ไม่พบลำดับเรื่องในระบบ โปรดใส่ให้พอดีกับเรื่องที่มีในระบบ"
                        )
                    else:
                        title = self.toolsmanhwa.showTitleFromNumber(
                            str(guild.id), int(title))
                        passForSend = True
                if passForSend:
                    check, args = self.toolsmanhwa.checkTitle(
                        str(guild.id), str(title))
                    if not check:
                        view = ButtonConfirmMannhwaSet(self.client, ctx, title,
                                                       chapter)
                        await interaction.response.send_message(
                            f"โปรดยืนยันรายการ manhwa ที่จะบันทึกข้อมูล\nชื่อเรื่อง '{title}' ตอนที่ '{chapter}' ยังไม่เคยมีอยู่ในระบบ\nถ้าต้องการจะบันทึก กดตกลงเพื่อบันทึกข้อมูล",
                            view=view)
                    else:
                        title = args
                        view = ButtonConfirmMannhwaSet(self.client, ctx, title,
                                                       chapter)
                        await interaction.response.send_message(
                            f"โปรดยืนยันรายการ manhwa ที่จะบันทึกข้อมูล\nชื่อเรื่อง '{title}' ตอนที่ '{chapter}' กดตกลงเพื่อบันทึกข้อมูล",
                            view=view)

    @app_commands.command(name="manhwa_remove",
                          description="ลบชื่อเรื่อง manhwa ในระบบ")
    @app_commands.choices(choices=[
        app_commands.Choice(name="ใส่ชื่อเรื่อง", value="1"),
        app_commands.Choice(name="ใส่ลำดับเรื่อง", value="2")
    ])
    @app_commands.describe(choices='ใส่ประเภทของข้อมูล')
    @app_commands.describe(title='ใส่ชื่อเรื่อง')
    async def manhwa_remove(self, interaction: Interaction,
                            choices: app_commands.Choice[str], title: str
                            or int):
        ctx = await self.client.get_context(interaction)
        guild = ctx.message.guild
        if str(guild.id) not in self.database:
            await interaction.response.send_message(
                "กรุณา setup ระบบในเซิร์ฟเวอร์นี้ก่อน")
        else:
            if "manhwa" not in self.database[str(guild.id)]:
                await interaction.response.send_message(
                    "กรุณาใช้คำสั่ง 'manhwa_setup' เพื่อ setup ระบบ manhwa ก่อนใช้งาน"
                )
            else:

                class ButtonConfirmMannhwaRemove(discord.ui.View):

                    def __init__(self, client, ctx: commands.Context,
                                 title: str):
                        super().__init__()
                        self.client = client
                        self.database = client.database
                        self.organize = client.organize
                        self.data = client.data

                    @discord.ui.button(label="ตกลง",
                                       style=discord.ButtonStyle.green)
                    async def button_confirm(self,
                                             interaction: discord.Interaction,
                                             button: discord.ui.Button):
                        for button in self.children:
                            button.disabled = True
                        await interaction.response.edit_message(view=self)
                        del self.database[str(
                            interaction.guild.id)]["manhwa"]["title"][title]
                        await ctx.send(
                            f"remove manhwa ชื่อเรื่อง '{title}' ออกจากระบบเสร็จสิ้น"
                        )

                    @discord.ui.button(label="ยกเลิก",
                                       style=discord.ButtonStyle.red)
                    async def button_cancel(self,
                                            interaction: discord.Interaction,
                                            button: discord.ui.Button):
                        for button in self.children:
                            button.disabled = True
                        await interaction.response.edit_message(view=self)
                        await ctx.send("ยกเลิกรายการ")

                passForSend = False
                if choices.value == '1':
                    passForSend = True
                elif choices.value == '2':
                    check = self.toolsmanhwa.checkNumber(str(guild.id), title)
                    if check == None:
                        await interaction.response.send_message(
                            f"คุณเลือกชนิดเป็นการใส่ลำดับเรื่อง โปรดระบุเป็นลำดับเลือกใหม่อีกครั้ง"
                        )
                    elif check == False:
                        await interaction.response.send_message(
                            f"ไม่พบลำดับเรื่องในระบบ โปรดใส่ให้พอดีกับเรื่องที่มีในระบบ"
                        )
                    else:
                        title = self.toolsmanhwa.showTitleFromNumber(
                            str(guild.id), int(title))
                        passForSend = True
                if passForSend:
                    check, args = self.toolsmanhwa.checkTitle(
                        str(guild.id), str(title))
                    if not check:
                        view = ButtonConfirmMannhwaRemove(
                            self.client, ctx, title)
                        await interaction.response.send_message(
                            f"ไม่พบ manhwa ชื่อเรื่อง '{title}' กรุณาลองใหม่อีกครั้ง"
                        )
                    else:
                        title = args
                        view = ButtonConfirmMannhwaRemove(
                            self.client, ctx, title)
                        await interaction.response.send_message(
                            f"โปรดยืนยันรายการ manhwa ที่จะลบข้อมูล\nชื่อเรื่อง '{title}' กดตกลงเพื่อลบข้อมูล",
                            view=view)


async def setup(client):
    await client.add_cog(Manhwa(client))
