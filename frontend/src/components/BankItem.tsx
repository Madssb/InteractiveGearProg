export type BankItemData = {
    name: string;
    imgUrl: string;
    wikiUrl?: string;
    quantity: number;
};

type BankItemProps = {
    item: BankItemData;
};

export default function BankItem({ item }: BankItemProps) {
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
