"use client";

import { useState } from "react";
import {
	Package,
	TruckIcon,
	CheckCircle2,
	Clock,
	MapPin,
	Phone,
	ChevronRight,
	Eye,
	Download,
} from "lucide-react";

// Mock orders data (in real app, fetch from API)
const mockOrders = [
	{
		id: "UG1704901234",
		date: "2025-01-10",
		status: "delivered",
		items: 2,
		total: 9850000,
		deliveryAddress: "Kampala, Central Region",
		estimatedDelivery: "2025-01-11",
		actualDelivery: "2025-01-11",
		trackingSteps: [
			{ status: "confirmed", time: "2025-01-10 14:30", completed: true },
			{ status: "processing", time: "2025-01-10 16:00", completed: true },
			{ status: "shipped", time: "2025-01-11 09:00", completed: true },
			{ status: "delivered", time: "2025-01-11 15:45", completed: true },
		],
		products: [
			{
				name: "iPhone 14 Pro 128GB",
				quantity: 1,
				price: 4500000,
				image: "https://images.unsplash.com/photo-1678652197831-2d180705cd2c?w=200&q=80",
			},
			{
				name: "MacBook Pro 14 M3",
				quantity: 1,
				price: 8500000,
				image: "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=200&q=80",
			},
		],
	},
	{
		id: "UG1704891234",
		date: "2025-01-08",
		status: "shipped",
		items: 1,
		total: 1200000,
		deliveryAddress: "Entebbe, Central Region",
		estimatedDelivery: "2025-01-12",
		trackingSteps: [
			{ status: "confirmed", time: "2025-01-08 10:15", completed: true },
			{ status: "processing", time: "2025-01-08 14:30", completed: true },
			{ status: "shipped", time: "2025-01-09 08:00", completed: true },
			{ status: "delivered", time: "", completed: false },
		],
		products: [
			{
				name: "Sony WH-1000XM5 Headphones",
				quantity: 1,
				price: 1200000,
				image: "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=200&q=80",
			},
		],
	},
	{
		id: "UG1704881234",
		date: "2025-01-05",
		status: "processing",
		items: 3,
		total: 2850000,
		deliveryAddress: "Jinja, Eastern Region",
		estimatedDelivery: "2025-01-14",
		trackingSteps: [
			{ status: "confirmed", time: "2025-01-05 16:45", completed: true },
			{ status: "processing", time: "2025-01-06 09:00", completed: true },
			{ status: "shipped", time: "", completed: false },
			{ status: "delivered", time: "", completed: false },
		],
		products: [
			{
				name: "Samsung Galaxy S23 Ultra",
				quantity: 1,
				price: 3800000,
				image: "https://images.unsplash.com/photo-1610945415295-d9bbf067e59c?w=200&q=80",
			},
		],
	},
];

type OrderStatus = "confirmed" | "processing" | "shipped" | "delivered";

const statusConfig: Record<OrderStatus, { label: string; color: string; icon: any }> = {
	confirmed: { label: "Order Confirmed", color: "bg-primary-100 text-primary-700", icon: CheckCircle2 },
	processing: { label: "Processing", color: "bg-warning-100 text-warning-700", icon: Clock },
	shipped: { label: "Shipped", color: "bg-accent-100 text-accent-700", icon: TruckIcon },
	delivered: { label: "Delivered", color: "bg-success-100 text-success-700", icon: Package },
};

export default function OrdersPage() {
	const [selectedOrder, setSelectedOrder] = useState<string | null>(null);

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		}).format(amount);
	};

	const formatDate = (dateString: string) => {
		return new Date(dateString).toLocaleDateString("en-UG", {
			day: "numeric",
			month: "short",
			year: "numeric",
		});
	};

	const order = mockOrders.find((o) => o.id === selectedOrder);

	return (
		<div className="min-h-screen bg-gray-50">
			<div className="container mx-auto px-4 py-6">
				{/* Breadcrumbs */}
				<nav className="flex items-center gap-2 text-sm text-gray-600 mb-6">
					<a href="/" className="hover:text-primary-600 transition-colors">
						Home
					</a>
					<ChevronRight size={16} />
					<span className="text-gray-900 font-medium">My Orders</span>
				</nav>

				{/* Header */}
				<div className="mb-8">
					<h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-2">
						My Orders
					</h1>
					<p className="text-gray-600">Track and manage your orders</p>
				</div>

				{!selectedOrder ? (
					/* Orders List */
					<div className="space-y-4">
						{mockOrders.map((order) => {
							const statusInfo = statusConfig[order.status as OrderStatus];
							const StatusIcon = statusInfo.icon;

							return (
								<div
									key={order.id}
									className="bg-white rounded-2xl shadow-card p-6 hover:shadow-lg transition-shadow"
								>
									<div className="flex flex-col lg:flex-row lg:items-center gap-6">
										{/* Order Info */}
										<div className="flex-1">
											<div className="flex items-center gap-3 mb-3">
												<span
													className={'px-3 py-1 rounded-full text-sm font-medium ' + statusInfo.color + ' flex items-center gap-2'}
												>
													<StatusIcon size={16} />
													{statusInfo.label}
												</span>
												<span className="text-gray-600 text-sm">
													{formatDate(order.date)}
												</span>
											</div>

											<p className="font-bold text-lg text-gray-900 mb-2">
												Order #{order.id}
											</p>

											<div className="grid sm:grid-cols-2 gap-2 text-sm text-gray-600">
												<div className="flex items-center gap-2">
													<Package size={16} />
													<span>{order.items} items</span>
												</div>
												<div className="flex items-center gap-2">
													<MapPin size={16} />
													<span>{order.deliveryAddress}</span>
												</div>
											</div>
										</div>

										{/* Order Total */}
										<div className="text-left lg:text-right">
											<p className="text-sm text-gray-600 mb-1">Total Amount</p>
											<p className="text-2xl font-bold text-primary-600">
												{formatPrice(order.total)}
											</p>
										</div>

										{/* Actions */}
										<div className="flex flex-col gap-2">
											<button
												onClick={() => setSelectedOrder(order.id)}
												className="px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
											>
												<Eye size={18} />
												View Details
											</button>
											{order.status === "delivered" && (
												<button className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-medium hover:border-primary-600 hover:text-primary-600 transition-colors flex items-center justify-center gap-2">
													<Download size={18} />
													Receipt
												</button>
											)}
										</div>
									</div>
								</div>
							);
						})}

						{mockOrders.length === 0 && (
							<div className="bg-white rounded-2xl shadow-card p-12 text-center">
								<div className="w-24 h-24 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
									<Package size={48} className="text-gray-400" />
								</div>
								<h3 className="text-xl font-bold text-gray-900 mb-2">
									No Orders Yet
								</h3>
								<p className="text-gray-600 mb-6">
									You have not placed any orders yet. Start shopping now!
								</p>
								<a
									href="/products"
									className="inline-block px-6 py-3 bg-primary-600 text-white rounded-xl font-medium hover:bg-primary-700 transition-colors"
								>
									Browse Products
								</a>
							</div>
						)}
					</div>
				) : (
					/* Order Detail View */
					<div>
						<button
							onClick={() => setSelectedOrder(null)}
							className="text-primary-600 hover:text-primary-700 font-medium flex items-center gap-2 mb-6"
						>
							Back to Orders
						</button>

						<div className="grid lg:grid-cols-3 gap-8">
							{/* Order Details */}
							<div className="lg:col-span-2 space-y-6">
								{/* Order Status */}
								<div className="bg-white rounded-2xl shadow-card p-8">
									<h2 className="text-2xl font-bold text-gray-900 mb-6">
										Order Status
									</h2>

									{/* Status Timeline */}
									<div className="space-y-6">
										{order?.trackingSteps.map((step, index) => {
											const stepInfo = statusConfig[step.status as OrderStatus];
											const StepIcon = stepInfo.icon;
											const isLast = index === order.trackingSteps.length - 1;

											return (
												<div key={step.status} className="flex gap-4">
													<div className="flex flex-col items-center">
														<div
															className={'w-12 h-12 rounded-full flex items-center justify-center ' + (step.completed ? "bg-success-600 text-white" : "bg-gray-200 text-gray-500")}
														>
															<StepIcon size={24} />
														</div>
														{!isLast && (
															<div
																className={'w-0.5 h-16 ' + (step.completed ? "bg-success-600" : "bg-gray-200")}
															/>
														)}
													</div>
													<div className="flex-1 pb-8">
														<p
															className={'font-bold ' + (step.completed ? "text-gray-900" : "text-gray-500")}
														>
															{stepInfo.label}
														</p>
														{step.time && (
															<p className="text-sm text-gray-600 mt-1">
																{new Date(step.time).toLocaleString("en-UG")}
															</p>
														)}
														{step.status === "delivered" && step.completed && (
															<p className="text-sm text-success-700 font-medium mt-2">
																Package delivered successfully
															</p>
														)}
													</div>
												</div>
											);
										})}
									</div>
								</div>

								{/* Order Items */}
								<div className="bg-white rounded-2xl shadow-card p-8">
									<h2 className="text-2xl font-bold text-gray-900 mb-6">
										Order Items
									</h2>
									<div className="space-y-4">
										{order?.products.map((product, index) => (
											<div
												key={index}
												className="flex gap-4 pb-4 border-b border-gray-200 last:border-0 last:pb-0"
											>
												<div className="relative w-20 h-20 flex-shrink-0 bg-gray-50 rounded-lg overflow-hidden">
													<img
														src={product.image}
														alt={product.name}
														className="w-full h-full object-contain p-2"
													/>
												</div>
												<div className="flex-1">
													<p className="font-bold text-gray-900">
														{product.name}
													</p>
													<p className="text-sm text-gray-600">
														Quantity: {product.quantity}
													</p>
													<p className="text-lg font-bold text-primary-600 mt-1">
														{formatPrice(product.price)}
													</p>
												</div>
											</div>
										))}
									</div>
								</div>
							</div>

							{/* Sidebar */}
							<div className="space-y-6">
								{/* Order Summary */}
								<div className="bg-white rounded-2xl shadow-card p-6">
									<h3 className="font-bold text-gray-900 mb-4">
										Order Information
									</h3>
									<div className="space-y-3 text-sm">
										<div>
											<p className="text-gray-600">Order ID</p>
											<p className="font-medium text-gray-900">{order?.id}</p>
										</div>
										<div>
											<p className="text-gray-600">Order Date</p>
											<p className="font-medium text-gray-900">
												{order && formatDate(order.date)}
											</p>
										</div>
										<div>
											<p className="text-gray-600">Total Amount</p>
											<p className="text-lg font-bold text-primary-600">
												{order && formatPrice(order.total)}
											</p>
										</div>
										<div>
											<p className="text-gray-600">Delivery Address</p>
											<p className="font-medium text-gray-900">
												{order?.deliveryAddress}
											</p>
										</div>
										<div>
											<p className="text-gray-600">Estimated Delivery</p>
											<p className="font-medium text-gray-900">
												{order && formatDate(order.estimatedDelivery)}
											</p>
										</div>
									</div>
								</div>

								{/* Help Section */}
								<div className="bg-primary-50 rounded-2xl p-6">
									<h3 className="font-bold text-gray-900 mb-3">Need Help?</h3>
									<p className="text-sm text-gray-700 mb-4">
										Contact our support team for any questions about your order.
									</p>
									<a
										href="tel:+256700000000"
										className="flex items-center gap-2 text-primary-600 hover:text-primary-700 font-medium"
									>
										<Phone size={18} />
										+256 700 000 000
									</a>
								</div>
							</div>
						</div>
					</div>
				)}
			</div>
		</div>
	);
}
