import React from "react";
import { Link } from "wouter";
import {
    Table,
    TableBody,
    TableCaption,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";

interface QnAProps {
    data: {
        id: number;
        q: string|null;
        a: string | null;
        category: string | null;
        filename: string | null;
    }[];
    loading: boolean;
}

const QnA: React.FC<QnAProps> = ({ data, loading }) => {
    return (
        <Table>
            <TableCaption>A list of your recent invoices.</TableCaption>
            <TableHeader>
                <TableRow>
                    <TableHead className="w-[100px]">ID</TableHead>
                    <TableHead>Question</TableHead>
                    <TableHead>Answer</TableHead>
                    <TableHead className="text-right">Category</TableHead>
                    <TableHead className="text-right">Filename</TableHead>
                </TableRow>
            </TableHeader>
            {loading ? (
                <TableBody>
                    <TableRow>
                        <TableCell className="font-medium">Loading...</TableCell>
                        <TableCell>Loading...</TableCell>
                        <TableCell>Loading...</TableCell>
                        <TableCell className="text-right">Loading...</TableCell>
                    </TableRow>
                </TableBody>
            ) : (
                <TableBody>
                    {data.map((item) => (
                        <TableRow key={item.id}>
                            <TableCell className="font-medium">
                                {item.id ? (
                                    <Link href={`/llm_frontend_proc_id/id/${item.id}`} className="text-blue-500 hover:text-blue-700">{item.id}</Link>
                                ) : (
                                    item.id
                                )}
                            </TableCell>
                            <TableCell>{item.q}</TableCell>
                            <TableCell>{item.a}</TableCell>
                            <TableCell className="text-right">
                                {item.category ? (
                                    <Link href={`/llm_frontend_proc_id/category/${item.category.replace(/ /g, '%%')}`} className="text-blue-500 hover:text-blue-700">
                                        {item.category}
                                    </Link>
                                ) : (
                                    item.category
                                )}
                            </TableCell>
                            <TableCell className="text-right">
                                {item.filename ? (
                                    <Link href={`/llm_frontend_proc_id/filename/${item.filename.split('.')[0]}`} className="text-blue-500 hover:text-blue-700">
                                        {item.filename.split('.')[0]}
                                    </Link>
                                ) : (
                                    item.filename
                                )}
                            </TableCell>
                        </TableRow>
                    ))}
                </TableBody>
            )}
        </Table>
    );
};

export default QnA;
