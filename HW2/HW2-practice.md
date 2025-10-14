[SQL Practice](https://www.w3schools.com/sql/trysql.asp?filename=trysql_select_join)

```sql
SELECT Orders.OrderID, Customers.CustomerName, Orders.OrderDate
FROM Orders
INNER JOIN Customers
ON Orders.CustomerID=Customers.CustomerID;
```

## Orders
OrderID	CustomerID	EmployeeID	OrderDate	ShipperID

## Customers
CustomerID	CustomerName	ContactName	Address	City	PostalCode	Country

## Shippers
ShipperID	ShipperName	Phone
