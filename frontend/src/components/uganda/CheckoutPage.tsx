"use client";

import { useState } from "react";
import Image from "next/image";
import {
	ChevronRight,
	ChevronLeft,
	MapPin,
	Phone,
	Mail,
	User,
	Home,
	CheckCircle2,
	Package,
	TruckIcon,
	CreditCard,
	Info,
} from "lucide-react";
import MobileMoneyPayment from "@/components/uganda/MobileMoneyPayment";
import DistrictSelector from "@/components/uganda/DistrictSelector";
import { mockFeaturedProducts, mockDistricts } from "@/lib/mock-data";

// Mock cart items (in real app, from state/API)
const mockCartItems = [
	{
		id: "cart-1",
		product: mockFeaturedProducts[0],
		quantity: 1,
	},
	{
		id: "cart-2",
		product: mockFeaturedProducts[1],
		quantity: 2,
	},
];

type CheckoutStep = "delivery" | "payment" | "confirmation";

interface DeliveryInfo {
	fullName: string;
	phone: string;
	email: string;
	district: typeof mockDistricts[0];
	address: string;
	landmark: string;
	deliveryNotes: string;
}

export default function CheckoutPage() {
	const [currentStep, setCurrentStep] = useState<CheckoutStep>("delivery");
	const [deliveryInfo, setDeliveryInfo] = useState<DeliveryInfo>({
		fullName: "",
		phone: "",
		email: "",
		district: mockDistricts[0],
		address: "",
		landmark: "",
		deliveryNotes: "",
	});
	const [orderId, setOrderId] = useState<string>("");

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
			maximumFractionDigits: 0,
		}).format(amount);
	};

	// Calculate totals
	const subtotal = mockCartItems.reduce(
		(sum, item) => sum + item.product.price * item.quantity,
		0
	);
	const deliveryFee = deliveryInfo.district.deliveryFee;
	const total = subtotal + deliveryFee;

	const handleDeliverySubmit = (e: React.FormEvent) => {
		e.preventDefault();
		setCurrentStep("payment");
	};

	const handlePaymentSuccess = () => {
		const newOrderId = `UG${Date.now()}`;
		setOrderId(newOrderId);
		setCurrentStep("confirmation");
	};

	const handlePaymentError = (error: string) => {
		alert(`Payment failed: ${error}. Please try again.`);
	};

	// Step indicator
	const steps = [
		{ key: "delivery", label: "Delivery", icon: TruckIcon },
		{ key: "payment", label: "Payment", icon: CreditCard },
		{ key: "confirmation", label: "Confirmation", icon: CheckCircle2 },
	];

	const currentStepIndex = steps.findIndex((s) => s.key === currentStep);

	return (
		<div className="min-h-screen bg-gray-50">
			<div className="container mx-auto px-4 py-6">
				{/* Breadcrumbs */}
				<nav className="flex items-center gap-2 text-sm text-gray-600 mb-6">
					<a href="/" className="hover:text-primary-600 transition-colors">
						Home
					</a>
					<ChevronRight size={16} />
					<a href="/cart" className="hover:text-primary-600 transition-colors">
						Cart
					</a>
					<ChevronRight size={16} />
					<span className="text-gray-900 font-medium">Checkout</span>
				</nav>

				{/* Header */}
				<div className="mb-8">
					<h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
						Checkout
					</h1>

					{/* Step Indicator */}
					<div className="flex items-center justify-center gap-4 max-w-2xl mx-auto">
						{steps.map((step, index) => {
							const Icon = step.icon;
							const isActive = currentStepIndex === index;
							const isCompleted = currentStepIndex > index;

							return (
								<div key={step.key} className="flex items-center flex-1">
									<div className="flex flex-col items-center flex-1">
										<div
											className={`w-12 h-12 rounded-full flex items-center justify-center transition-colors ${
												isCompleted
													? "bg-success-600 text-white"
													: isActive
													? "bg-primary-600 text-white"
													: "bg-gray-200 text-gray-500"
											}`}
										>
											<Icon size={24} />
										</div>
										<span
											className={`mt-2 text-sm font-medium ${
												isActive || isCompleted
													? "text-gray-900"
													: "text-gray-500"
											}`}
										>
											{step.label}
										</span>
									</div>
									{index < steps.length - 1 && (
										<div
											className={`flex-1 h-1 mx-2 transition-colors ${
												isCompleted ? "bg-success-600" : "bg-gray-200"
											}`}
										/>
									)}
								</div>
							);
						})}
					</div>
				</div>

				<div className="grid lg:grid-cols-3 gap-8">
					{/* Main Content */}
					<div className="lg:col-span-2">
						{/* Delivery Form */}
						{currentStep === "delivery" && (
							<div className="bg-white rounded-3xl shadow-card p-8">
								<h2 className="text-2xl font-bold text-gray-900 mb-6">
									Delivery Information
								</h2>
								<form onSubmit={handleDeliverySubmit} className="space-y-6">
									{/* Full Name */}
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-2">
											Full Name <span className="text-error-600">*</span>
										</label>
										<div className="relative">
											<User
												size={20}
												className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
											/>
											<input
												type="text"
												required
												value={deliveryInfo.fullName}
												onChange={(e) =>
													setDeliveryInfo({
														...deliveryInfo,
														fullName: e.target.value,
													})
												}
												placeholder="Enter your full name"
												className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-600"
											/>
										</div>
									</div>

									{/* Phone & Email */}
									<div className="grid md:grid-cols-2 gap-4">
										<div>
											<label className="block text-sm font-medium text-gray-700 mb-2">
												Phone Number <span className="text-error-600">*</span>
											</label>
											<div className="relative">
												<Phone
													size={20}
													className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
												/>
												<input
													type="tel"
													required
													value={deliveryInfo.phone}
													onChange={(e) =>
														setDeliveryInfo({
															...deliveryInfo,
															phone: e.target.value,
														})
													}
													placeholder="256XXXXXXXXX"
													className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-600"
												/>
											</div>
										</div>
										<div>
											<label className="block text-sm font-medium text-gray-700 mb-2">
												Email Address
											</label>
											<div className="relative">
												<Mail
													size={20}
													className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
												/>
												<input
													type="email"
													value={deliveryInfo.email}
													onChange={(e) =>
														setDeliveryInfo({
															...deliveryInfo,
															email: e.target.value,
														})
													}
													placeholder="your@email.com"
													className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-600"
												/>
											</div>
										</div>
									</div>

									{/* District */}
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-2">
											Delivery District <span className="text-error-600">*</span>
										</label>
										<DistrictSelector
											districts={mockDistricts}
											selectedDistrict={deliveryInfo.district}
											onSelect={(district) =>
												setDeliveryInfo({ ...deliveryInfo, district })
											}
										/>
									</div>

									{/* Address */}
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-2">
											Street Address <span className="text-error-600">*</span>
										</label>
										<div className="relative">
											<Home
												size={20}
												className="absolute left-4 top-4 text-gray-400"
											/>
											<textarea
												required
												value={deliveryInfo.address}
												onChange={(e) =>
													setDeliveryInfo({
														...deliveryInfo,
														address: e.target.value,
													})
												}
												placeholder="Building name, floor, apartment number"
												rows={3}
												className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-600 resize-none"
											/>
										</div>
									</div>

									{/* Landmark */}
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-2">
											Nearby Landmark
										</label>
										<div className="relative">
											<MapPin
												size={20}
												className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400"
											/>
											<input
												type="text"
												value={deliveryInfo.landmark}
												onChange={(e) =>
													setDeliveryInfo({
														...deliveryInfo,
														landmark: e.target.value,
													})
												}
												placeholder="E.g., Near City Square Mall"
												className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-600"
											/>
										</div>
									</div>

									{/* Delivery Notes */}
									<div>
										<label className="block text-sm font-medium text-gray-700 mb-2">
											Delivery Notes (Optional)
										</label>
										<div className="relative">
											<Info
												size={20}
												className="absolute left-4 top-4 text-gray-400"
											/>
											<textarea
												value={deliveryInfo.deliveryNotes}
												onChange={(e) =>
													setDeliveryInfo({
														...deliveryInfo,
														deliveryNotes: e.target.value,
													})
												}
												placeholder="Any special instructions for delivery"
												rows={3}
												className="w-full pl-12 pr-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-600 resize-none"
											/>
										</div>
									</div>

									<button
										type="submit"
										className="w-full bg-primary-600 text-white py-4 rounded-xl font-bold text-lg hover:bg-primary-700 transition-colors flex items-center justify-center gap-2"
									>
										Continue to Payment
										<ChevronRight size={24} />
									</button>
								</form>
							</div>
						)}

						{/* Payment Step */}
						{currentStep === "payment" && (
							<div className="bg-white rounded-3xl shadow-card p-8">
								<div className="mb-6">
									<button
										onClick={() => setCurrentStep("delivery")}
										className="text-primary-600 hover:text-primary-700 font-medium flex items-center gap-2 mb-4"
									>
										<ChevronLeft size={20} />
										Back to Delivery
									</button>
									<h2 className="text-2xl font-bold text-gray-900">
										Payment Method
									</h2>
								</div>

								<MobileMoneyPayment
									amount={total}
									orderId={`ORDER-${Date.now()}`}
									onSuccess={handlePaymentSuccess}
									onError={handlePaymentError}
								/>
							</div>
						)}

						{/* Confirmation Step */}
						{currentStep === "confirmation" && (
							<div className="bg-white rounded-3xl shadow-card p-8 text-center">
								<div className="w-24 h-24 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-6">
									<CheckCircle2 size={56} className="text-success-600" />
								</div>
								<h2 className="text-3xl font-bold text-gray-900 mb-4">
									Order Confirmed!
								</h2>
								<p className="text-gray-600 mb-2">
									Thank you for your purchase, {deliveryInfo.fullName}!
								</p>
								<p className="text-gray-600 mb-8">
									Your order <span className="font-bold">{orderId}</span> has been
									placed successfully.
								</p>

								<div className="bg-primary-50 rounded-2xl p-6 mb-8 text-left">
									<h3 className="font-bold text-gray-900 mb-4 flex items-center gap-2">
										<Package size={20} className="text-primary-600" />
										Order Details
									</h3>
									<div className="space-y-2 text-sm text-gray-700">
										<div className="flex justify-between">
											<span>Order ID:</span>
											<span className="font-medium">{orderId}</span>
										</div>
										<div className="flex justify-between">
											<span>Items:</span>
											<span className="font-medium">
												{mockCartItems.length} products
											</span>
										</div>
										<div className="flex justify-between">
											<span>Total Paid:</span>
											<span className="font-bold text-primary-600">
												{formatPrice(total)}
											</span>
										</div>
										<div className="flex justify-between">
											<span>Delivery to:</span>
											<span className="font-medium">
												{deliveryInfo.district.name}
											</span>
										</div>
										<div className="flex justify-between">
											<span>Estimated Delivery:</span>
											<span className="font-medium">
												{deliveryInfo.district.estimatedDays} days
											</span>
										</div>
									</div>
								</div>

								<div className="bg-accent-50 rounded-2xl p-6 mb-8 text-left">
									<h3 className="font-bold text-gray-900 mb-3">What's Next?</h3>
									<ul className="space-y-2 text-sm text-gray-700">
										<li className="flex items-start gap-2">
											<span className="text-success-600 mt-0.5">✓</span>
											<span>
												You'll receive an SMS confirmation shortly at{" "}
												{deliveryInfo.phone}
											</span>
										</li>
										<li className="flex items-start gap-2">
											<span className="text-success-600 mt-0.5">✓</span>
											<span>
												Track your order status in the "My Orders" section
											</span>
										</li>
										<li className="flex items-start gap-2">
											<span className="text-success-600 mt-0.5">✓</span>
											<span>
												Our delivery team will contact you before delivery
											</span>
										</li>
									</ul>
								</div>

								<div className="flex flex-col sm:flex-row gap-4">
									<a
										href="/orders"
										className="flex-1 bg-primary-600 text-white py-4 rounded-xl font-bold hover:bg-primary-700 transition-colors"
									>
										View My Orders
									</a>
									<a
										href="/products"
										className="flex-1 border-2 border-gray-300 text-gray-700 py-4 rounded-xl font-bold hover:border-primary-600 hover:text-primary-600 transition-colors"
									>
										Continue Shopping
									</a>
								</div>
							</div>
						)}
					</div>

					{/* Order Summary Sidebar */}
					<div>
						<div className="bg-white rounded-3xl shadow-card p-6 sticky top-6">
							<h3 className="font-bold text-gray-900 mb-4">Order Summary</h3>

							{/* Cart Items */}
							<div className="space-y-4 mb-6 max-h-64 overflow-y-auto">
								{mockCartItems.map((item) => (
									<div key={item.id} className="flex gap-4">
										<div className="relative w-16 h-16 flex-shrink-0 bg-gray-50 rounded-lg overflow-hidden">
											<Image
												src={item.product.image}
												alt={item.product.name}
												fill
												className="object-contain p-2"
											/>
										</div>
										<div className="flex-1">
											<p className="text-sm font-medium text-gray-900 line-clamp-2">
												{item.product.name}
											</p>
											<p className="text-sm text-gray-600">Qty: {item.quantity}</p>
											<p className="text-sm font-bold text-gray-900">
												{formatPrice(item.product.price * item.quantity)}
											</p>
										</div>
									</div>
								))}
							</div>

							{/* Totals */}
							<div className="border-t border-gray-200 pt-4 space-y-3 text-sm">
								<div className="flex justify-between text-gray-700">
									<span>Subtotal</span>
									<span className="font-medium">{formatPrice(subtotal)}</span>
								</div>
								<div className="flex justify-between text-gray-700">
									<span>Delivery Fee</span>
									<span className="font-medium">{formatPrice(deliveryFee)}</span>
								</div>
								<div className="border-t border-gray-200 pt-3 flex justify-between text-lg">
									<span className="font-bold">Total</span>
									<span className="font-bold text-primary-600">
										{formatPrice(total)}
									</span>
								</div>
							</div>
						</div>
					</div>
				</div>
			</div>
		</div>
	);
}
