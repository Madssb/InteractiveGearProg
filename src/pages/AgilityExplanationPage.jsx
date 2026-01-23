import '@/styles/agility-explanation.css';
import '@/styles/theme.css';

export default function AgilityExplanationPage() {
  return (
    <>
      <h1>Why is 98 agility on the PVM chart?</h1>
      <p>
        Hallowed Sepulchre is uniquely strong for ironman progression, yielding much more than just agility xp.
        <i>Assuming you 98 agility anyways</i>, sepulchre is very strong in the early game, netting tons of resources and exp in other skills, enabling other powerful unlocks early game.
      </p>

      <h2>Raw coins and runes</h2>
      <p>
        Sepulchre sources important and expensive runes. A large portion of the law rune stack can even comfortably be sold for significant gp.
      </p>
      <ul className="icon-list">
        <li>
          <img src="../images/Coins_10000.webp" alt="Coins" />
          <span><span className="green-text">24.5m</span> gp</span>
        </li>
        <li>
          <img src="../images/Blood_rune.webp" alt="Blood rune" />
          <span><span className="white-text">44.7k</span> blood runes (<span className="green-text">17.9m</span> gp cost)</span>
        </li>
        <li>
          <img src="../images/Soul_rune.webp" alt="Soul rune" />
          <span><span className="white-text">44.7k</span> soul runes (<span className="green-text">15.0m</span> gp cost)</span>
        </li>
        <li>
          <img src="../images/Law_rune.webp" alt="Law rune" />
          <span>44.7k law runes (<span className="white-text">8.9m</span> gp cost, <span className="white-text">5.4m</span> gained if sold)</span>
        </li>
        <li>
          <img src="../images/Death_rune.webp" alt="Death rune" />
          <span>8.1k death runes (<span className="white-text">1.6m</span> gp cost)</span>
        </li>
        <li>
          <img src="../images/Cosmic_rune.webp" alt="Cosmic rune" />
          <span>6.1k cosmic runes (<span className="white-text">340k</span> gp cost)</span>
        </li>
      </ul>

      <span>
        Total: <span className="green-text">64.8m</span> coins. (~81 hours of air battlestaves, 5.6m crafting)
      </span>

      <h2>Prayer potions</h2>
      <p></p>

      <h2>Experience</h2>
      <p>
        Sepulchre levels not only agility, but also thieving, construction, and magic. Furthermore, it provides near ideal conditions to also multiskill fletching and alchs.
      </p>
      <ul className="icon-list">
        <li>
          <img src="../images/Thieving_icon.webp" alt="Thieving" />
          <span>565k Thieving XP</span>
        </li>
        <li>
          <img src="../images/Construction_icon.webp" alt="Construction" />
          <span>444k Construction XP</span>
        </li>
        <li>
          <img src="../images/Fletching_icon.webp" alt="Fletching" />
          <span>~600k Fletching XP (headless arrow / broad arrow, multiskilled)</span>
        </li>
        <li>
          <img src="../images/Magic_icon.webp" alt="Magic" />
          <span>~3.2m Magic XP (Alchs, multiskilled)</span>
        </li>
      </ul>

      <h2>Cost of skipping</h2>
      <p>82-98 agility is a 129 hour grind which by conventional standards is pretty long.</p>
      <p>
        <a href="https://docs.google.com/spreadsheets/d/1orNUuGmhMWQamytxwrVyZI_c6fLWZH4J0yJX1nRLgXM/edit?gid=0#gid=0">
          source
        </a>
      </p>
    </>
  );
}
