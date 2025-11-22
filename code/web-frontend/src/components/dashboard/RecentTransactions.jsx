import React from 'react';
import {
    Box,
    Typography,
    Card,
    CardContent,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TableRow,
} from '@mui/material';

const RecentTransactions = ({ transactions }) => {
    // Default values if transactions aren't provided
    const defaultTransactions = [
        { date: '2025-04-05', asset: 'AAPL', type: 'Buy', amount: '$2,500.00' },
        { date: '2025-04-01', asset: 'TSLA', type: 'Sell', amount: '$1,800.00' },
        { date: '2025-03-28', asset: 'BTC', type: 'Buy', amount: '$1,000.00' },
        { date: '2025-03-15', asset: 'MSFT', type: 'Buy', amount: '$3,200.00' },
        { date: '2025-03-10', asset: 'GLD', type: 'Sell', amount: '$2,100.00' },
    ];

    const data = transactions || defaultTransactions;

    return (
        <Card>
            <CardContent>
                <Typography variant="h6" gutterBottom>
                    Recent Transactions
                </Typography>

                <TableContainer>
                    <Table size="small">
                        <TableHead>
                            <TableRow>
                                <TableCell>Date</TableCell>
                                <TableCell>Asset</TableCell>
                                <TableCell>Type</TableCell>
                                <TableCell align="right">Amount</TableCell>
                            </TableRow>
                        </TableHead>
                        <TableBody>
                            {data.map((transaction, index) => (
                                <TableRow key={index}>
                                    <TableCell>{transaction.date}</TableCell>
                                    <TableCell>{transaction.asset}</TableCell>
                                    <TableCell>
                                        <Typography
                                            variant="body2"
                                            color={
                                                transaction.type === 'Buy'
                                                    ? 'success.main'
                                                    : 'error.main'
                                            }
                                        >
                                            {transaction.type}
                                        </Typography>
                                    </TableCell>
                                    <TableCell align="right">{transaction.amount}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </TableContainer>
            </CardContent>
        </Card>
    );
};

export default RecentTransactions;
