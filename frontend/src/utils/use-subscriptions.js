import React, { useState } from "react";
import api from '../api'

export default function useSubscriptions () {
  const [ subscriptions, setSubscriptions ] = useState([])
  const [ subscriptionsPage, setSubscriptionsPage ] = useState(1)
  const [ subscriptionsCount, setSubscriptionsCount ] = useState(0)

  const removeSubscription = ({ id, callback }) => {
    api
      .deleteSubscriptions({ author_id: id })
      .then(res => {
        const subscriptionsUpdated = subscriptions.filter(item => {
          return item.id !== id
        })
        setSubscriptions(subscriptionsUpdated)
        setSubscriptionsCount(subscriptionsCount - 1)
        callback && callback()
      })
      .catch(err => {
        const { errors } = err
        if (errors) {
          alert(errors)
        }
      })
  }

  const getSubscriptions = ({ page = 1, limit = 6, recipes_limit = 3 }) => {
    api
      .getSubscriptions({ page, limit, recipes_limit })
      .then(res => {
        const { results = [], count = 0 } = res || {}
        setSubscriptions(Array.isArray(results) ? results : [])
        setSubscriptionsCount(count)
      })
      .catch(err => {
        console.error('Error fetching subscriptions in useSubscriptions:', err)
        setSubscriptions([])
        setSubscriptionsCount(0)
      })
  }
  
  return {
    subscriptions,
    setSubscriptions,
    subscriptionsPage,
    setSubscriptionsPage,
    removeSubscription,
    subscriptionsCount,
    setSubscriptionsCount,
    getSubscriptions
  }
}
