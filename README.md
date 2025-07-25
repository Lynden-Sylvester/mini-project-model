# Mini Project Model Example

## Purpose
The purpose of this project is to highlight an issue that occurs between the asyncio-v3.4.3 library and the AsyncIOScheduler from APScheduler (version 3.11.0) when passing a `job.id` into a synchronous function call being run in an `asyncio.to_thread()` where the job is created in the AsyncIOScheduler AFTER the asyncio thread has called the synchronous function that needs the `job.id`

## How To Set up
1. Clone this repository to your IDE of choice
2. Open the `.env` file. You need to configure this file.
<br><p>2a. Go to <a href="https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwj8raiEjtSOAxUeSzABHVD_JacQFnoECAoQAQ&url=https%3A%2F%2Fdiscord.com%2Fdevelopers%2Fapplications&usg=AOvVaw1wrZe_Tr9Sav0Zx4-42-Jf&opi=89978449">Discord Developer Portal</a> and create a new Application. Name it whatever you want. Just make sure you enable the following Privelaged intents:
    <ul>
        <ol>
            - Mesage Content Intent
        </ol>
        <ol>
            - Server Members Intent
        </ol>
    </ul>
    and the following values from your bot map to the `.env` like this:
    <ul>
        <ol>
            - APP_ID= Application ID
        </ol>
        <ol>
            - CLIENT_SECRET = Client Secret
        </ol>
        <ol>
            - BOT_SECRET = Token
        </ol>
    </ul>
    Also make sure when generating the OAuth2 Url, that you check the `bot` scope and the following bot permissions:
    <ul>
        <ol>
            - View Channels
        </ol>
        <ol>
            - Read Message History
        </ol>
        <ol>
            - Send Mesages
        </ol>
    </ul>
            You can now install the bot as a Guild install
</p>
<p>2b. In discord under `User Setting > App Setings > Advanced`, make sure Developer Mode is on. Then go to the discord server you installed the bot on, and right click on the server name, and select `Copy Server ID`. Paste this value into the `.env` assigned to `GUILD_ID`.

In discord, pick a ROLE in your discord server with the ADMINISTRATOR perms, and type in a text channel `\@rolename`, this'll give you output like this: `<@123456789012345678>`. Take ONLY the numbers, and paste it in the `.env` assigned to `ADMIN_ROLE_ID`

Now you're ready.
</p>

3. There's a couple more steps to go through before we get the Error in console.
<p>
    <u;>
        <ol> First, in your IDE's terminal, run `main.py`, this starts the scheduler and the bot. </ol>
        <ol>Next, go to discord and type `#sync` this will manually sync all the application commands.</ol>
        <ol>Next type `/sync` and refresh discord with `CMD + R`</ol>
        <ol>Next run `/admin guild_init`. Set your guild_key to whatever you want. This will set up a folder structure in your IDE for your guild with a guild db, and a settings yml file.</ol>
        <ol>Finally, run `/admin db` with the option set to `Create`, and you can name the db_name whatever you want. When you run this, it will fail and spit out the error stacktrace in your IDE's Console</ol>
    </ul>
</p>