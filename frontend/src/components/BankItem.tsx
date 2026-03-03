type ItemInfo = {
    imgUrl: string,
    wikiUrl: string,
    quantity: BigInteger
}


export default function BankItem({ item }) {
    return (
        <a
            className="bank-item"
            href={item.wikiUrl || "#"}
            target={item.wikiUrl ? "_blank" : "_self"}
            rel="noreferrer"
            title={item.name}
        >
            <img src={item.imgUrl} alt={item.name} />
            <span>{item.quantity}</span>
        </a>
    );
}
