import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface Position {
  symbol: string;
  current_value: number;
}

interface AllocationChartProps {
  positions: Position[];
}

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];


const AllocationChart = ({ positions }: AllocationChartProps) => {
    const data = positions.map(pos => ({
        name: pos.symbol,
        value: pos.current_value,
    }));

    const renderLabel = (entry: any) => {
        const percent = (entry.percent * 100).toFixed(1);
        return `${entry.name} (${percent}%)`;
    };

    return (
        <ResponsiveContainer width="100%" height={400}>
            <PieChart>
                <Pie
                    data={data}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={80}
                    label={renderLabel}
                    labelLine={true}
                >
                    {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                </Pie>
                <Tooltip formatter={(value: number) => `$${value.toFixed(2)}`} />
            </PieChart>
        </ResponsiveContainer>
    );
};

export default AllocationChart;