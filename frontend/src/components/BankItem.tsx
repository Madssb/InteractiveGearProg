export type BankItemData = {
    name: string;
    imgUrl: string;
    quantity: number;
};

type BankItemProps = {
    item: BankItemData;
};

export default function BankItem({ item }: BankItemProps) {
    return (
        <div className="bank-item" title={item.name}>
            <img src={item.imgUrl} alt={item.name} />
            <span>{item.quantity}</span>
        </div>
    );
}
