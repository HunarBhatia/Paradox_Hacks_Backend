from django.core.management.base import BaseCommand
from stories.models import Story


STORIES = [
    {
        "trader_name": "Rakesh Jhunjhunwala",
        "title": "How Rakesh Jhunjhunwala Built His Empire",
        "content": "Rakesh Jhunjhunwala started investing with just ₹5,000 in 1985 while still a student. Against his father's wishes, he pursued the stock market with relentless conviction. His early bet on Tata Tea multiplied his capital manifold and gave him the confidence to go bigger.\n\nOver decades, he built a portfolio worth billions, earning the title 'Big Bull of India'. His most famous bet was on Titan Company, where he held through massive volatility and was rewarded beyond imagination.\n\nHe believed in India's growth story before most did, and that faith became the foundation of every trade he made.",
        "famous_quote": "I am bullish on India. If India grows, my investments will grow.",
        "key_lesson": "Bet big on conviction, hold through volatility, and trust the long-term story.",
        "image_url": "",
    },
    {
        "trader_name": "Warren Buffett",
        "title": "The Oracle of Omaha's Path to $100 Billion",
        "content": "Warren Buffett bought his first stock at age 11 and filed his first tax return at 13. By the time he was 30, he had already built a small fortune through his investment partnership, using Benjamin Graham's value investing principles as his foundation.\n\nBuffett's genius was in evolving — he moved from pure Graham-style deep value to buying wonderful businesses at fair prices, largely influenced by Charlie Munger. His purchase of Coca-Cola in 1988 and Apple decades later showed his ability to adapt.\n\nHis secret was simple: buy businesses you understand, run by people you trust, at prices that make sense. Then do nothing.",
        "famous_quote": "The stock market is a device for transferring money from the impatient to the patient.",
        "key_lesson": "Buy great businesses at fair prices and hold them for decades.",
        "image_url": "",
    },
    {
        "trader_name": "Peter Lynch",
        "title": "How Peter Lynch Turned Magellan into a Legend",
        "content": "Peter Lynch managed the Fidelity Magellan Fund from 1977 to 1990, delivering a 29% average annual return — one of the best track records in history. His edge? He invested in what he knew and understood from everyday life.\n\nLynch coined the idea of 'investing in your backyard' — if you noticed a great product or restaurant before Wall Street did, you had an edge. He discovered multi-baggers like Dunkin' Donuts and L'eggs simply by observing consumer trends.\n\nHe categorized stocks into slow growers, stalwarts, fast growers, cyclicals, turnarounds, and asset plays — giving retail investors a practical framework to think like a pro.",
        "famous_quote": "Invest in what you know.",
        "key_lesson": "Everyday observations can lead to extraordinary investment opportunities.",
        "image_url": "",
    },
    {
        "trader_name": "Jesse Livermore",
        "title": "The Boy Plunger Who Moved Markets",
        "content": "Jesse Livermore started trading at 15 in bucket shops, reading ticker tape with uncanny accuracy. By his early twenties he had been banned from most shops for winning too consistently. He moved to Wall Street and made — and lost — multiple fortunes.\n\nHis greatest trade came during the 1929 crash. Livermore shorted the market and made $100 million in a single day, equivalent to billions today. He had studied the market's behavior for months before pulling the trigger.\n\nYet discipline was his eternal struggle. He broke his own rules, overtrade, and eventually lost everything. His life is the ultimate lesson: even the best system fails without ironclad discipline.",
        "famous_quote": "The market is never wrong. Opinions often are.",
        "key_lesson": "A great strategy means nothing without the discipline to follow it.",
        "image_url": "",
    },
    {
        "trader_name": "Benjamin Graham",
        "title": "The Father of Value Investing",
        "content": "Benjamin Graham lived through the 1929 crash and lost nearly everything. That experience forged his obsession with margin of safety — never pay more for a stock than it's worth, and always leave a buffer for being wrong.\n\nHis book 'The Intelligent Investor' became the bible of value investing, influencing generations of investors including Warren Buffett, who called it the best book on investing ever written. Graham's framework of Mr. Market — the irrational neighbor who offers to buy or sell every day — taught investors to use market volatility rather than fear it.\n\nGraham proved that investing could be a disciplined, analytical process rather than speculation.",
        "famous_quote": "The investor's chief problem — and even his worst enemy — is likely to be himself.",
        "key_lesson": "Always invest with a margin of safety and never let emotions drive decisions.",
        "image_url": "",
    },
    {
        "trader_name": "George Soros",
        "title": "The Man Who Broke the Bank of England",
        "content": "George Soros is best known for one of the most audacious trades in history — shorting the British pound in 1992. He studied the fundamentals, concluded the UK could not sustain its position in the European Exchange Rate Mechanism, and bet $10 billion against the pound.\n\nWhen Britain was forced to devalue and exit the ERM, Soros made over $1 billion in a single day. The trade earned him the title 'The Man Who Broke the Bank of England.'\n\nSoros operates on his theory of reflexivity — markets are not efficient because participants' biases affect the very fundamentals they are trying to analyze. Understanding feedback loops between perception and reality is his edge.",
        "famous_quote": "It's not whether you're right or wrong, but how much money you make when you're right and how much you lose when you're wrong.",
        "key_lesson": "Position sizing and knowing when you're right matters more than just being right.",
        "image_url": "",
    },
    {
        "trader_name": "Charlie Munger",
        "title": "The Architect of Buffett's Best Decisions",
        "content": "Charlie Munger spent his early career as a lawyer before turning to investing. He brought a multidisciplinary approach to Berkshire Hathaway — applying mental models from psychology, physics, biology, and economics to investing decisions.\n\nIt was Munger who pushed Buffett to evolve from Graham's cigar-butt investing to buying wonderful companies at fair prices. His influence is behind many of Berkshire's greatest investments including See's Candies, a business that taught them the power of brand and pricing power.\n\nMunger's latticework of mental models — inversion, second-order thinking, circle of competence — became a philosophy for thinking clearly in any domain.",
        "famous_quote": "Invert, always invert. Turn a situation or problem upside down.",
        "key_lesson": "Build a latticework of mental models to make better decisions in investing and life.",
        "image_url": "",
    },
    {
        "trader_name": "Vijay Kedia",
        "title": "From Loss to Legend — Vijay Kedia's Comeback Story",
        "content": "Vijay Kedia started investing in the 1990s and suffered devastating losses early on, nearly wiping out his family's capital. Most would have quit. Instead, he studied his mistakes obsessively and rebuilt his approach from scratch.\n\nHe developed his SMILE framework — Small in size, Medium in experience, Large in aspiration, and Extra-large in market potential. He applied this to find unknown, under-researched companies before they became mainstream.\n\nHis bets on companies like Atul Auto and Aegis Logistics turned modest investments into life-changing returns. Kedia's story is proof that recovery from failure, combined with a clear framework, is more valuable than never failing at all.",
        "famous_quote": "I look for small companies with big dreams.",
        "key_lesson": "A clear investment framework and the courage to recover from failure define great investors.",
        "image_url": "",
    },
    {
        "trader_name": "Ramesh Damani",
        "title": "The Calm Bull Who Saw India's Potential Early",
        "content": "Ramesh Damani returned from the US in the early 1990s to invest in India's stock market at a time when most educated Indians were heading the other way. He saw the liberalization of the economy as a historic opportunity and positioned himself accordingly.\n\nHe made early bets on technology and consumption themes in India, riding multi-decade trends with patience few investors can maintain. His calm, measured demeanor became his trademark — never panicking, never chasing, always thinking in decades.\n\nDamani is also known for mentoring a generation of Indian investors and emphasizing that the biggest risk in investing is not being invested in a growing economy.",
        "famous_quote": "The biggest risk is not taking any risk in a bull market.",
        "key_lesson": "Think in decades, not days — and stay invested in a growing economy.",
        "image_url": "",
    },
    {
        "trader_name": "Mohnish Pabrai",
        "title": "The Dhandho Investor Who Cloned His Way to Wealth",
        "content": "Mohnish Pabrai built his fortune by doing something counterintuitive — he openly copied the best ideas of the world's greatest investors. He called it cloning, and he applied it with rigorous discipline through his Pabrai Investment Funds.\n\nHis Dhandho framework, inspired by Indian Patel motel owners, boiled investing down to: heads I win, tails I don't lose much. He looked for bets with asymmetric risk-reward, low downside, and massive upside.\n\nPabrai also famously paid $650,000 to have lunch with Warren Buffett, calling it the best investment he ever made. His transparency, humility, and systematic approach have made him one of the most respected value investors of his generation.",
        "famous_quote": "Heads I win, tails I don't lose much.",
        "key_lesson": "Seek asymmetric bets where downside is limited but upside is enormous.",
        "image_url": "",
    },
]


class Command(BaseCommand):
    help = "Seed trader stories into the database"

    def handle(self, *args, **kwargs):
        count = 0
        for data in STORIES:
            _, created = Story.objects.get_or_create(
                trader_name=data["trader_name"],
                defaults=data
            )
            if created:
                count += 1
                self.stdout.write(f"  Added: {data['trader_name']}")
            else:
                self.stdout.write(f"  Skipped (exists): {data['trader_name']}")

        self.stdout.write(self.style.SUCCESS(f"\nDone. {count} new stories added."))