"use client";

import { useState } from "react";
import { Smartphone, CheckCircle, XCircle, Loader2 } from "lucide-react";
import Image from "next/image";

type Provider = "mtn_momo" | "airtel_money" | "cash_on_delivery";
type PaymentStatus = "idle" | "initiating" | "pending" | "successful" | "failed";

interface MobileMoneyPaymentProps {
	amount: number;
	orderId: string;
	onSuccess: (transactionId: string) => void;
	onError: (error: string) => void;
}

export default function MobileMoneyPayment({
	amount,
	orderId,
	onSuccess,
	onError,
}: MobileMoneyPaymentProps) {
	const [selectedProvider, setSelectedProvider] = useState<Provider | null>(null);
	const [phoneNumber, setPhoneNumber] = useState("");
	const [status, setStatus] = useState<PaymentStatus>("idle");
	const [transactionId, setTransactionId] = useState("");

	const formatPrice = (amount: number) => {
		return new Intl.NumberFormat("en-UG", {
			style: "currency",
			currency: "UGX",
			minimumFractionDigits: 0,
		}).format(amount);
	};

	const formatPhoneNumber = (value: string) => {
		// Remove non-digits
		const digits = value.replace(/\D/g, "");

		// Format as Uganda number
		if (digits.startsWith("256")) {
			return digits.slice(0, 12);
		} else if (digits.startsWith("0")) {
			return "256" + digits.slice(1, 10);
		} else {
			return "256" + digits.slice(0, 9);
		}
	};

	const handlePhoneChange = (e: React.ChangeEvent<HTMLInputElement>) => {
		const formatted = formatPhoneNumber(e.target.value);
		setPhoneNumber(formatted);
	};

	const displayPhoneNumber = (number: string) => {
		if (!number) return "";
		if (number.startsWith("256")) {
			return "+256 " + number.slice(3);
		}
		return number;
	};

	const handlePayment = async () => {
		if (!selectedProvider || !phoneNumber) return;

		if (selectedProvider === "cash_on_delivery") {
			// Handle cash on delivery
			setStatus("successful");
			onSuccess("COD-" + Date.now());
			return;
		}

		try {
			setStatus("initiating");

			// Call backend API to initiate payment
			const response = await fetch("/api/payments/mobile-money", {
				method: "POST",
				headers: { "Content-Type": "application/json" },
				body: JSON.stringify({
					provider: selectedProvider,
					phoneNumber,
					amount,
					orderId,
				}),
			});

			if (!response.ok) {
				throw new Error("Failed to initiate payment");
			}

			const data = await response.json();
			setTransactionId(data.transactionId);
			setStatus("pending");

			// Poll for payment status
			pollPaymentStatus(data.transactionId);
		} catch (error) {
			setStatus("failed");
			onError(error instanceof Error ? error.message : "Payment failed");
		}
	};

	const pollPaymentStatus = async (txId: string) => {
		let attempts = 0;
		const maxAttempts = 60; // 5 minutes (5s intervals)

		const poll = async () => {
			if (attempts >= maxAttempts) {
				setStatus("failed");
				onError("Payment timeout - please try again");
				return;
			}

			try {
				const response = await fetch(`/api/payments/status/${txId}`);
				const data = await response.json();

				if (data.status === "successful") {
					setStatus("successful");
					onSuccess(txId);
				} else if (data.status === "failed") {
					setStatus("failed");
					onError(data.message || "Payment failed");
				} else {
					// Still pending, poll again
					attempts++;
					setTimeout(poll, 5000);
				}
			} catch (error) {
				setStatus("failed");
				onError("Failed to check payment status");
			}
		};

		poll();
	};

	return (
		<div className="bg-white rounded-2xl shadow-lg p-6">
			<h2 className="text-2xl font-bold text-gray-900 mb-2">Choose Payment Method</h2>
			<p className="text-gray-600 mb-6">
				Total Amount: <span className="text-2xl font-bold text-primary-600 font-mono">{formatPrice(amount)}</span>
			</p>

			{/* Provider Selection */}
			<div className="space-y-3 mb-6">
				{/* MTN Mobile Money */}
				<button
					onClick={() => setSelectedProvider("mtn_momo")}
					disabled={status === "pending"}
					className={`w-full flex items-center justify-between p-4 border-2 rounded-xl transition-all ${
						selectedProvider === "mtn_momo"
							? "border-success-500 bg-success-50"
							: "border-gray-200 hover:border-success-300"
					} ${status === "pending" ? "opacity-50 cursor-not-allowed" : ""}`}
				>
					<div className="flex items-center gap-3">
						<div className="w-12 h-12 bg-success-500 rounded-lg flex items-center justify-center">
							<span className="text-2xl font-bold text-gray-900">M</span>
						</div>
						<div className="text-left">
							<p className="font-bold text-gray-900">MTN Mobile Money</p>
							<p className="text-sm text-gray-600">Pay with MTN MoMo</p>
						</div>
					</div>
					{selectedProvider === "mtn_momo" && (
						<span className="text-success-600 font-semibold">✓ Selected</span>
					)}
				</button>

				{/* Airtel Money */}
				<button
					onClick={() => setSelectedProvider("airtel_money")}
					disabled={status === "pending"}
					className={`w-full flex items-center justify-between p-4 border-2 rounded-xl transition-all ${
						selectedProvider === "airtel_money"
							? "border-error-500 bg-error-50"
							: "border-gray-200 hover:border-error-300"
					} ${status === "pending" ? "opacity-50 cursor-not-allowed" : ""}`}
				>
					<div className="flex items-center gap-3">
						<div className="w-12 h-12 bg-error-500 rounded-lg flex items-center justify-center">
							<span className="text-2xl font-bold text-white">A</span>
						</div>
						<div className="text-left">
							<p className="font-bold text-gray-900">Airtel Money</p>
							<p className="text-sm text-gray-600">Pay with Airtel Money</p>
						</div>
					</div>
					{selectedProvider === "airtel_money" && (
						<span className="text-error-600 font-semibold">✓ Selected</span>
					)}
				</button>

				{/* Cash on Delivery */}
				<button
					onClick={() => setSelectedProvider("cash_on_delivery")}
					disabled={status === "pending"}
					className={`w-full flex items-center justify-between p-4 border-2 rounded-xl transition-all ${
						selectedProvider === "cash_on_delivery"
							? "border-primary-500 bg-primary-50"
							: "border-gray-200 hover:border-primary-300"
					} ${status === "pending" ? "opacity-50 cursor-not-allowed" : ""}`}
				>
					<div className="flex items-center gap-3">
						<div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
							<span className="text-2xl">💵</span>
						</div>
						<div className="text-left">
							<p className="font-bold text-gray-900">Cash on Delivery</p>
							<p className="text-sm text-gray-600">Pay when you receive (+UGX 5,000 fee)</p>
						</div>
					</div>
					{selectedProvider === "cash_on_delivery" && (
						<span className="text-primary-600 font-semibold">✓ Selected</span>
					)}
				</button>
			</div>

			{/* Phone Number Input */}
			{selectedProvider && selectedProvider !== "cash_on_delivery" && (
				<div className="mb-6">
					<label className="block text-sm font-semibold text-gray-900 mb-2">
						<Smartphone className="inline mr-1" size={16} />
						Enter Phone Number
					</label>
					<input
						type="tel"
						value={displayPhoneNumber(phoneNumber)}
						onChange={handlePhoneChange}
						placeholder="+256 700 123 456"
						disabled={status === "pending"}
						className="w-full px-4 py-3 border-2 border-gray-200 rounded-xl focus:outline-none focus:border-primary-500 text-lg font-mono disabled:bg-gray-50"
					/>
					<p className="text-xs text-gray-600 mt-2">
						Enter the number registered with {selectedProvider === "mtn_momo" ? "MTN" : "Airtel"} Mobile Money
					</p>
				</div>
			)}

			{/* Payment Status */}
			{status !== "idle" && (
				<div className={`mb-6 p-4 rounded-xl ${
					status === "successful" ? "bg-green-50 border-2 border-green-200" :
					status === "failed" ? "bg-error-50 border-2 border-error-200" :
					"bg-blue-50 border-2 border-blue-200"
				}`}>
					{status === "initiating" && (
						<div className="flex items-center gap-3">
							<Loader2 className="animate-spin text-blue-600" size={24} />
							<p className="text-blue-900 font-semibold">Initiating payment...</p>
						</div>
					)}
					{status === "pending" && (
						<div>
							<div className="flex items-center gap-3 mb-2">
								<Loader2 className="animate-spin text-blue-600" size={24} />
								<p className="text-blue-900 font-semibold">Waiting for payment...</p>
							</div>
							<p className="text-sm text-blue-700">
								📱 Check your phone for the payment prompt from{" "}
								{selectedProvider === "mtn_momo" ? "MTN" : "Airtel"}
							</p>
							<p className="text-sm text-blue-700 mt-1">
								Enter your PIN to complete the payment
							</p>
						</div>
					)}
					{status === "successful" && (
						<div className="flex items-center gap-3">
							<CheckCircle className="text-green-600" size={24} />
							<div>
								<p className="text-green-900 font-semibold">Payment Successful!</p>
								<p className="text-sm text-green-700">Transaction ID: {transactionId}</p>
							</div>
						</div>
					)}
					{status === "failed" && (
						<div className="flex items-center gap-3">
							<XCircle className="text-error-600" size={24} />
							<p className="text-error-900 font-semibold">Payment Failed - Please try again</p>
						</div>
					)}
				</div>
			)}

			{/* Submit Button */}
			<button
				onClick={handlePayment}
				disabled={!selectedProvider || (selectedProvider !== "cash_on_delivery" && !phoneNumber) || status === "pending"}
				className="w-full bg-primary-600 text-white py-4 rounded-xl font-bold text-lg hover:bg-primary-700 transition-colors disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center justify-center gap-2"
			>
				{status === "pending" ? (
					<>
						<Loader2 className="animate-spin" size={24} />
						Processing...
					</>
				) : (
					<>
						{selectedProvider === "cash_on_delivery" ? "Confirm Order" : "Pay Now"}
					</>
				)}
			</button>

			{/* Trust Badges */}
			<div className="mt-6 pt-6 border-t border-gray-100">
				<div className="flex items-center justify-center gap-6 text-sm text-gray-600">
					<span className="flex items-center gap-1">
						🔒 Secure Payment
					</span>
					<span className="flex items-center gap-1">
						✓ Verified Merchant
					</span>
					<span className="flex items-center gap-1">
						📱 SMS Confirmation
					</span>
				</div>
			</div>
		</div>
	);
}
